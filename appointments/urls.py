from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    # ── Doctors ──────────────────────────────────────────────────
    path("doctors/", views.DoctorListView.as_view(), name="doctor-list"),
    path("doctors/<int:pk>/", views.DoctorDetailView.as_view(), name="doctor-detail"),
    path("doctors/<int:pk>/availability/", views.DoctorAvailabilityView.as_view(), name="doctor-availability"),

    # ── Appointments ─────────────────────────────────────────────
    path("", views.AppointmentListView.as_view(), name="appointment-list"),
    path("book/", views.BookAppointmentView.as_view(), name="appointment-book"),
    path("<int:pk>/", views.AppointmentDetailView.as_view(), name="appointment-detail"),
    path("<int:pk>/cancel/", views.CancelAppointmentView.as_view(), name="appointment-cancel"),
    path("<int:pk>/reschedule/", views.RescheduleAppointmentView.as_view(), name="appointment-reschedule"),
]
