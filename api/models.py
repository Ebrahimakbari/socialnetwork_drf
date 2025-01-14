import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
from .managers import CustomUserManager,PostManager
from django.utils.text import slugify
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
        


class Post(models.Model):
    PUBLISHED = 'PUB'
    PRIVATE = 'PRI'
    
    publish_status = [
        (PUBLISHED,'published'),
        (PRIVATE,'private'),
    ]
    
    author = models.ForeignKey(CustomUser, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    image = models.ImageField(upload_to='articles/')
    slug = models.SlugField(blank=True, null=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=publish_status,default=PUBLISHED)
    
    objects = models.Manager()
    published = PostManager()

    class Meta:
        verbose_name = ("Post")
        verbose_name_plural = ("Posts")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    
    def save(self):
        self.slug = slugify(self.title)
        return super().save()
    
    def get_likes_count(self):
        return self.likes.filter(is_liked=True).count()
    
    
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    reply = models.ForeignKey(
        "self",
        related_name="replys",
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    is_reply = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ("Comment")
        verbose_name_plural = ("Comments")

    def __str__(self):
        return f'{self.user} on post {self.post}'


class PostLike(models.Model):
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)    

    class Meta:
        verbose_name = ("PostLike")
        verbose_name_plural = ("PostLikes")

    def __str__(self):
        return f'user {self.user} liked post {self.post}'


class Relation(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='followings', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='follower', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ("Relation")
        verbose_name_plural = ("Relations")

    def __str__(self):
        return f'{self.from_user} following {self.to_user}'