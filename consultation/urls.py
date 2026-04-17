from django.urls import path
from . import views

app_name = "consultation"

urlpatterns = [
    path("<int:pk>/join/",           views.JoinConsultationView.as_view(),      name="consultation-join"),
    path("<int:pk>/start/",          views.StartConsultationView.as_view(),     name="consultation-start"),
    path("<int:pk>/end/",            views.EndConsultationView.as_view(),       name="consultation-end"),
    path("<int:pk>/notes/",          views.AddConsultationNoteView.as_view(),   name="consultation-notes"),
    path("onboarding/personal/",     views.OnboardingPersonalView.as_view(),    name="onboarding-personal"),
    path("onboarding/professional/", views.OnboardingProfessionalView.as_view(),name="onboarding-professional"),
    path("onboarding/medical-info/", views.OnboardingMedicalInfoView.as_view(), name="onboarding-medical-info"),
    path("onboarding/availability/", views.OnboardingAvailabilityView.as_view(),name="onboarding-availability"),
    path("onboarding/documents/",    views.OnboardingDocumentsView.as_view(),   name="onboarding-documents"),
    path("onboarding/status/",       views.OnboardingStatusView.as_view(),      name="onboarding-status"),
    path("onboarding/resubmit/",     views.OnboardingResubmitView.as_view(),    name="onboarding-resubmit"),
    path("doctors/",                 views.DoctorListView.as_view(),            name="doctor-list"),
    path("doctors/<int:pk>/",        views.DoctorDetailView.as_view(),          name="doctor-detail"),
]



