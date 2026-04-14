from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', views.CookieTokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', views.AuthTokenVerifyView.as_view(), name='token-verify'),
    path('me/', views.MeView.as_view(), name='me'),
    path('verify-otp/', views.VerifyOtpView.as_view(), name='verify-otp'),
    path('resend-otp/', views.ResendOtpView.as_view(), name='resend-otp'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/personal/', views.PersonalInformationView.as_view(), name='profile-personal'),
    path('profile/medical/', views.MedicalInformationView.as_view(), name='profile-medical'),
    path('profile/emergency/', views.EmergencyContactView.as_view(), name='profile-emergency'),
]
