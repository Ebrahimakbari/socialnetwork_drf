from rest_framework import serializers
from .models import Post, Comment, PostLike, Relation
from django.utils.text import slugify
from rest_framework_simplejwt.tokens import RefreshToken
from .authentications import authenticate
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomUserInfoSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    follower = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

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
            "first_name",
            "last_name",
            "likes",
            "info",
            "comments",
            "followings",
            "follower",
            "posts",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "full_name",
            "is_active",
            "likes",
            "comments",
            "followings",
            "follower",
            "posts",
        ]

    def get_likes(self,obj):
        return PostLikeSerializer(instance=obj.likes.all(), many=True, context=self.context).data
    
    def get_comments(self,obj):
        return CommentSerializer(instance=obj.comments.all(), many=True, context=self.context).data

    def get_follower(self,obj):
        return RelationSerializer(instance=obj.follower.all(), many=True, context=self.context).data

    def get_followings(self,obj):
        return RelationSerializer(instance=obj.followings.all(), many=True, context=self.context).data

    def get_posts(self,obj):
        return PostSerializer(instance=obj.posts.all(), many=True, context=self.context).data


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
            access["email"] = user.email

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


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.IntegerField(source="get_likes_count", read_only=True)
    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "content",
            "slug",
            "image",
            "likes_count",
            "created_at",
            "updated_at",
            "status",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user
        return Post.objects.create(**validated_data)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replays = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "post",
            "reply",
            "is_reply",
            "content",
            "created_at",
            "replays",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    # To fetch nested replies
    def get_replays(self, obj):
        if obj.is_reply:
            return None
        qs = obj.replys.all()
        return CommentSerializer(instance=qs, many=True, context=self.context).data

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class PostLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    is_liked = serializers.BooleanField(required=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = PostLike
        fields = [
            'id',
            'user',
            'post',
            'is_liked',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
        ]
    
    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        representations = super().to_representation(instance)
        representations['post'] = PostSerializer(instance=instance.post, context=self.context).data
        return representations


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = [
            'from_user',
            'to_user',
            'created',
        ]
        read_only_fields = [
            'created',
            'from_user',
        ]
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['from_user'] = request.user
        return super().create(validated_data)