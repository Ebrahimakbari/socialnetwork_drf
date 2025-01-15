from django.urls import path
from . import views
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'posts', views.PostViewSet, basename='posts')

urlpatterns = [
    path('sign-up/', views.UserSignupView.as_view(), name='sign_up'),
    path('activate/<int:user_id>/<str:token>/', views.UserActivationRequestView.as_view(), name='activate'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/<int:user_id>/<str:token>/', views.PasswordResetView.as_view(), name='password-reset-request'),
    path('user-info/', views.UserInfoView.as_view(), name='user-info'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('access-token/', views.GetAccessToken.as_view(), name='get-access'),
]

urlpatterns += router.urls