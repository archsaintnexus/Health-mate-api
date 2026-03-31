from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('verify-otp/', views.VerifyOtpView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOtpView.as_view(), name='resend-otp'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/personal/', views.PersonalInformationView.as_view(), name='profile-personal'),
    path('profile/medical/', views.MedicalInformationView.as_view(), name='profile-medical'),
    path('profile/emergency/', views.EmergencyContactView.as_view(), name='profile-emergency'),
]
