from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.UserSignupView.as_view(), name='sign_up'),
    path('activate/<int:user_id>/<str:token>/', views.UserActivationRequestView.as_view(), name='activate'),
    path('login/', views.UserLoginView.as_view(), name='login'),
]
