from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


def authenticate(email=None, password=None):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise serializers.ValidationError('user with that email does not exists!!')
    if user.check_password(password):
        return user
    return None