from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Task(models.Model):
    name = models.CharField('Name', max_length=25)
    description = models.CharField('Description', max_length=150)
    time_created = models.DateTimeField('Time created', auto_now_add=True, editable=False)
    progress = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ]
    )
    completed = models.BooleanField('Completed', default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.name


class Message(models.Model):
    subject = models.CharField('Subject', max_length=25)
    body = models.CharField('Body', max_length=100)
    time_created = models.DateTimeField('Time created', auto_now_add=True, editable=False)
    read = models.BooleanField('Read', default=False)
    user_from = models.ForeignKey(User, related_name='user_from', on_delete=models.PROTECT)
    user_to = models.ForeignKey(User, related_name='user_to', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return self.subject


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen = models.DateTimeField('Last seen', null=True)
    photo = models.ImageField('User photo', upload_to='users_photo', blank=True, null=True)
    email_confirmed = models.BooleanField('Email confirmed', default=False)

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'Users profiles'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
