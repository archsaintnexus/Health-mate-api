from django.urls import path
from . import views

app_name = "medicals"

urlpatterns = [
    # ── Medical Records ───────────────────────────────────────
    path(
        "records/",
        views.MedicalRecordListView.as_view(),
        name="record-list"
    ),
    path(
        "records/<int:pk>/",
        views.MedicalRecordDetailView.as_view(),
        name="record-detail"
    ),
    path(
        "records/<int:pk>/prescriptions/<int:prescription_id>/send-to-pharmacy/",
        views.SendPrescriptionToPharmacyView.as_view(),
        name="send-to-pharmacy"
    ),

    # ── Lab Tests ─────────────────────────────────────────────
    path(
        "lab-tests/",
        views.LabTestListView.as_view(),
        name="lab-test-list"
    ),
    path(
        "lab-tests/<int:pk>/",
        views.LabTestDetailView.as_view(),
        name="lab-test-detail"
    ),
]