from rest_framework import serializers
from .models import Post, Comment, PostLike, Relation
from django.db.models import F
from rest_framework_simplejwt.tokens import RefreshToken
from .authentications import authenticate
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomUserInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "is_active",
            "phone_number",
            "avatar",
            'first_name',
            'last_name',
            'info'
        ]
        read_only_fields = [
            'id',
            'username',
            'email',
            'full_name',
            'is_active',
        ]


class UserSignUpSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("mismatch passwords!!")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        return super().create(validated_data)


class UserActivationRequestSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()

    def validate(self, attrs):
        token = attrs["token"]
        user_id = attrs["user_id"]
        users = User.objects.filter(pk=user_id, token=token)
        if users.exists():
            user = users.first()
            user.is_active = True
            user.token = ""
            user.save()
            return attrs
        raise serializers.ValidationError("invalid token!!")


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]
        user = authenticate(email, password)
        if user and user.is_active:
            refresh = RefreshToken.for_user(user=user)
            access = refresh.access_token
            # add extra field to payload of jwt
            access['email'] = user.email
            
            attrs["user"] = user
            attrs["refresh"] = str(refresh)
            attrs["access"] = str(access)
            return attrs
        raise serializers.ValidationError("email or password incorrect!!")


class UserLoginResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    email = serializers.EmailField()
    access = serializers.CharField()
    refresh = serializers.CharField()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        user = User.objects.filter(email=attrs["email"])
        if user.exists():
            attrs["user"] = user.first()
            return attrs
        raise serializers.ValidationError("email not found!!")


class PasswordResetCheckSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.IntegerField()

    def validate(self, attrs):
        token = attrs["token"]
        user_id = attrs["user_id"]
        users = User.objects.filter(pk=user_id, token=token)
        if users.exists():
            attrs["user"] = users.first()
            return attrs
        raise serializers.ValidationError("invalid token!!")


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password = attrs["password"]
        password2 = attrs["password2"]
        email = attrs["email"]
        user = User.objects.filter(email=email)
        if password and password2 and password2 == password and user.exists():
            user = user.first()
            user.set_password(password)
            user.token = ""
            user.save()
            return attrs
        raise serializers.ValidationError(
            "passwords should be same with correct combination of email and user_id"
        )
