"""DjangoDemo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_TITLE_HEADER

handler404 = 'apps.main.views_errors.handler404'
handler500 = 'apps.main.views_errors.handler500'

urlpatterns = [
    path('login', auth_views.LoginView.as_view(), name="login"),
    path('logout', auth_views.LogoutView.as_view(), name="logout"),
    path('password-reset', auth_views.PasswordResetView.as_view(
         template_name='registration/password/password_reset_form.html',
         email_template_name='email/password_reset_email.html',
         subject_template_name='email/password_reset_subject.txt'),
         name='password-reset'),
    path('password-reset-done', auth_views.PasswordResetDoneView.as_view(
         template_name='registration/password/password_reset_done.html'),
         name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('reset/done', auth_views.PasswordResetCompleteView.as_view(
         template_name='registration/password/password_reset_complete.html'),
         name='password_reset_complete'),
    path('', include('apps.main.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
