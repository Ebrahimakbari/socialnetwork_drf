import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
from .managers import CustomUserManager
# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.IntegerField(blank=True, null=True)
    avatar = models.ImageField(upload_to='media/user/',blank=True, null=True)
    info = models.TextField(blank=True,null=True)
    is_active = models.BooleanField(default=False)
    token = models.CharField(max_length=100, null=True, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    class Meta:
        verbose_name = ("User")
        verbose_name_plural = ("Users")

    def __str__(self):
        return self.email

    def send_email(self, request, action):
        """Send an email to this user.
        action=activate/reset-password"""
        reset_token = str(uuid.uuid4())
        self.token = reset_token
        self.save()
        reset_link = f"http://{request.get_host()}/{action}/{self.pk}/{reset_token}/"
        subject = f'{action} User Account'
        message = f'Click the link to for {action} : {reset_link}'
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [self.email])
