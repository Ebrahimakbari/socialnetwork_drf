from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.UserSignupView.as_view(), name='sign_up'),
    path('activate/<int:user_id>/<str:token>/', views.UserActivationRequestView.as_view(), name='activate'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('reset-password/<int:user_id>/<str:token>/', views.PasswordResetView.as_view(), name='password-reset-request'),
    path('user-info/', views.UserInfoView.as_view(), name='user-info'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
