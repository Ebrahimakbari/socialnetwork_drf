from rest_framework import views, viewsets,generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Comment, PostLike
from .serializers import (
    UserSignUpSerializer,
    UserActivationRequestSerializer,
    CustomUserInfoSerializer,
    UserLoginSerializer,
    UserLoginResponseSerializer,
    PasswordResetRequestSerializer,
    PasswordResetCheckSerializer,
    PasswordResetSerializer,
    PostSerializer,
    CommentSerializer,
    PostLikeSerializer
)


User = get_user_model()


class UserSignupView(views.APIView):
    def post(self, request):
        srz_data = UserSignUpSerializer(data=request.data)
        if srz_data.is_valid():
            user_instance = srz_data.save()
            user_instance.send_email(request, action="activate")
            data = {
                "message": "user created check your email box to activate your account!",
                "data": srz_data.data,
            }

            return Response(data=data, status=status.HTTP_201_CREATED)
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivationRequestView(views.APIView):
    def get(self, request, user_id, token):
        data = {"token": token, "user_id": user_id}
        srz_data = UserActivationRequestSerializer(data=data)
        if srz_data.is_valid():
            user_id = srz_data.validated_data["user_id"]
            user = User.objects.get(pk=user_id)
            user_info = CustomUserInfoSerializer(instance=user)
            data = {"data": user_info.data, "message": "user activated successfully!"}

            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(views.APIView):
    def post(self, request):
        srz_data = UserLoginSerializer(data=request.data)
        if srz_data.is_valid():
            user_data = {
                "user_id": srz_data.validated_data["user"].pk,
                "email": srz_data.validated_data["user"].email,
                "access": srz_data.validated_data["access"],
                "refresh": srz_data.validated_data["refresh"],
            }

            res_data = UserLoginResponseSerializer(data=user_data)
            res_data.is_valid(raise_exception=True)
            return Response(data=res_data.data, status=status.HTTP_200_OK)
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAccessToken(views.APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                data={"message": "refresh token is required!!!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh)
            access = refresh.access_token
            refresh.set_jti()  # generate new refresh token
            data = {"access": str(access), "refresh": str(refresh)}
            return Response(data=data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(data={"message": e}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(views.APIView):
    def post(self, request):
        srz_data = PasswordResetRequestSerializer(data=request.data)
        if srz_data.is_valid():
            user = srz_data.validated_data["user"]
            user.send_email(request, action="reset-password")
            data = {
                "message": "a link to reset password sent to your email!!",
                "data": srz_data.data,
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(views.APIView):
    def get(self, request, user_id, token):
        data = {"user_id": user_id, "token": token}
        srz_data = PasswordResetCheckSerializer(data=data)
        if srz_data.is_valid():
            data = {
                "message": (
                    "your token is valid! now you can send post request to this endpoint to reset password!"
                ),
                "data": srz_data.data,
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        srz_data = PasswordResetSerializer(data=request.data)
        token = kwargs.get("token")
        user_id = kwargs.get("user_id")
        user = User.objects.filter(token=token, pk=user_id)
        if user.exists() and srz_data.is_valid():
            data = {"message": "passwords changed successfully!", "data": srz_data.data}
            return Response(data=data, status=status.HTTP_202_ACCEPTED)
        data = {
            "message": (
                "tokens are disposable!!"
                if not user.exists()
                else "invalid password or email!"
            ),
            "data": srz_data.errors if srz_data.is_valid(raise_exception=False) else "",
        }
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(views.APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
                return Response(
                    {"message": "you logged out!!"}, status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {"message": f"{e} invalid refresh token!!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"message": "refresh token is required!!"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserInfoView(views.APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        srz_data = CustomUserInfoSerializer(instance=user)
        return Response(data=srz_data.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        srz_data = CustomUserInfoSerializer(
            instance=user, data=request.data, partial=True
        )
        if srz_data.is_valid():
            srz_data.save()
            return Response(data=srz_data.data, status=status.HTTP_202_ACCEPTED)
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.published.all()
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticated,
    ]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticated,
    ]


class PostLikeViewSet(viewsets.ModelViewSet):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    permission_classes = [
        IsAuthenticated,
    ]
