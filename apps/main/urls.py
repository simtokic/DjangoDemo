from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('users', views.UsersView.as_view(), name='users'),
    path('tasks', views.TasksView.as_view(), name='tasks'),
    path('inbox', views.InboxMessagesView.as_view(), name='inbox-messages'),
    path('sent', views.SentMessagesView.as_view(), name='sent-messages'),
    path('create-task', views.CreateTaskView.as_view(), name='create-task'),
    path('create-message', views.CreateMessageView.as_view(),
         name='create-message'),
    path('edit-task/<int:pk>', views.UpdateTaskView.as_view(), name='edit-task'),
    path('message-details/<int:pk>', views.DetailMessageView.as_view(), name='message-details'),
    path('profile', views.update_profile, name='profile'),
    path('register', views.register, name='register'),
    path('account-activation-sent', views.AccountActivationSent.as_view(),
         name='account-activation-sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
