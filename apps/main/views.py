from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from .forms import ProfileForm, SignUpForm, UserForm
from .models import Message, Task
from .tokens import account_activation_token


@method_decorator(login_required, name='dispatch')
class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['users_count'] = User.objects.count()
        context['tasks_count'] = Task.objects.count()
        context['tasks_completed_count'] = Task.objects.filter(Q(completed=True) | Q(progress=100))
        context['messages_count'] = Message.objects.count()
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class UsersView(ListView):
    model = User
    paginate_by = settings.PAGINATE_BY
    template_name = 'main/users.html'

    def get_queryset(self):
        return User.objects.all().order_by('id')

    def get_context_data(self, **kwargs):
        context = super(UsersView, self).get_context_data(**kwargs)
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class TasksView(ListView):
    model = Task
    paginate_by = settings.PAGINATE_BY
    template_name = 'main/tasks/tasks.html'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-time_created')

    def get_context_data(self, **kwargs):
        context = super(TasksView, self).get_context_data(**kwargs)
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class InboxMessagesView(ListView):
    model = Message
    paginate_by = settings.PAGINATE_BY
    template_name = 'main/messages/inbox_messages.html'

    def get_queryset(self):
        return Message.objects.filter(user_to=self.request.user).order_by('-time_created')

    def get_context_data(self, **kwargs):
        context = super(InboxMessagesView, self).get_context_data(**kwargs)
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class SentMessagesView(ListView):
    model = Message
    paginate_by = settings.PAGINATE_BY
    template_name = 'main/messages/sent_messages.html'

    def get_queryset(self):
        return Message.objects.filter(user_from=self.request.user).order_by('-time_created')

    def get_context_data(self, **kwargs):
        context = super(SentMessagesView, self).get_context_data(**kwargs)
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class CreateTaskView(CreateView):
    model = Task
    fields = ['name', 'description']
    template_name = 'main/tasks/create_task.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateTaskView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateTaskView, self).get_context_data(**kwargs)
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class CreateMessageView(CreateView):
    model = Message
    fields = ['user_to', 'subject', 'body']
    template_name = 'main/messages/create_message.html'
    success_url = reverse_lazy('sent-messages')

    def form_valid(self, form):
        form.instance.user_from = self.request.user
        return super(CreateMessageView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreateMessageView, self).get_context_data(**kwargs)
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class UpdateTaskView(UpdateView):
    model = Task
    fields = ['name', 'description', 'progress', 'completed']
    template_name = 'main/tasks/edit_task.html'
    success_url = reverse_lazy('tasks')

    def get_object(self, queryset=None):
        return Task.objects.get(user=self.request.user, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        common_context(context, self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class DetailMessageView(DetailView):
    template_name = 'main/messages/message_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inbox'] = self.inbox
        common_context(context, self.request.user)

        # Mark as read
        self.object.read = True
        self.object.save()

        return context

    def get_queryset(self):
        message = Message.objects.filter(Q(user_to=self.request.user) | Q(user_from=self.request.user),
                                         pk=self.kwargs['pk'])

        if message.count() > 0 and message[0].user_from == self.request.user:
            self.inbox = False
        elif message.count() > 0:
            self.inbox = True

        return message


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('home')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.userprofile)

    context = {}
    context['user_form'] = user_form
    context['profile_form'] = profile_form

    common_context(context, request.user)

    return render(request, 'main/profile/user_profile.html', context)


@transaction.atomic
def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Django Demo Account'
            message = render_to_string('email/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
            })
            user.email_user(subject, message)
            return redirect('account-activation-sent')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


@transaction.atomic
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.userprofile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'registration/activation/account_activation_invalid.html')


class AccountActivationSent(TemplateView):
    template_name = 'registration/activation/account_activation_sent.html'


def common_context(context, user):
    context['my_tasks'] = Task.objects.filter(user=user, completed=False).order_by('-time_created')
    context['my_messages'] = Message.objects.filter(user_to=user, read=False).order_by('-time_created')
