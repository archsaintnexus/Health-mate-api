from django.urls import path
from . import views

app_name = "consultation"

urlpatterns = [
    # ── Consultations ─────────────────────────────────────────────
    path("", views.ConsultationListView.as_view(), name="consultation-list"),
    path("<int:pk>/", views.ConsultationDetailView.as_view(), name="consultation-detail"),
    path("<int:pk>/join/", views.JoinConsultationView.as_view(), name="consultation-join"),
    path("<int:pk>/start/", views.StartConsultationView.as_view(), name="consultation-start"),
    path("<int:pk>/end/", views.EndConsultationView.as_view(), name="consultation-end"),
    path("<int:pk>/cancel/", views.CancelConsultationView.as_view(), name="consultation-cancel"),
    path("<int:pk>/notes/", views.AddConsultationNoteView.as_view(), name="consultation-notes"),
]
