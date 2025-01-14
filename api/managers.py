from django.contrib.auth.models import UserManager
from django.db import models
from django.db.models import Q


class CustomUserManager(UserManager):
    def create(self, email, username, password, **extra_fields):
        return self.create_user(email, username, password, **extra_fields)
    
    def create_user(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)
    

class PostManager(models.Manager):
    def get_queryset(self,*args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(status='PUB')
    
    def search(self,q, *args, **kwargs):
        return self.get_queryset(*args, **kwargs).filter(
            Q(title__icontains=q) | Q(content__icontains=q)
            )
