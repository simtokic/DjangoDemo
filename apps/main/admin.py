from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Message, Task, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'time_created', 'progress', 'completed', 'user')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'time_created', 'read', 'user_from', 'user_to')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Message, MessageAdmin)
