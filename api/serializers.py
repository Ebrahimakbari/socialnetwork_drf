from rest_framework import serializers
from .models import Post,Comment,PostLike,Relation
from django.db.models import F
from rest_framework_simplejwt.tokens import RefreshToken
from .authentications import authenticate
from django.contrib.auth import get_user_model


User = get_user_model()



class CustomUserInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name')
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'is_active', 'phone_number', 'avatar']


class UserSignUpSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('mismatch passwords!!')
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return super().create(validated_data)


class UserActivationRequestSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()

    def validate(self, attrs):
        token = attrs['token']
        user_id = attrs['user_id']
        users = User.objects.filter(pk=user_id, token=token)
        if users.exists():
            user = users.first()
            user.is_active = True
            user.token = ''
            user.save()
            return attrs
        raise serializers.ValidationError('invalid token!!')


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs['email']
        password = attrs['password']
        user = authenticate(email, password)
        if user and user.is_active:
            refresh = RefreshToken.for_user(user=user)
            attrs['user'] = user
            attrs['refresh'] = str(refresh)
            attrs['access'] = str(refresh.access_token)
            return attrs
        raise serializers.ValidationError('email or password incorrect!!') 
            

class UserLoginResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    email = serializers.EmailField()
    access = serializers.CharField()
    refresh = serializers.CharField()


