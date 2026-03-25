from django.urls import path
from .views import (ProviderSearchView, ProviderDetailView, ProviderSlotsView, BookAppointmentView, MyAppointmentsView,
AppointmentDetailView, CancelAppointmentView,
)

urlpatterns = [
    # Provider endpoints
    path('providers/', ProviderSearchView.as_view(), name='provider-search'),
    path('providers/<int:provider_id>/', ProviderDetailView.as_view(), name='provider-detail'), # This queries using provider_id.
    path('providers/<int:provider_id>/slots/', ProviderSlotsView.as_view(), name='provider-slots'),

    # Appointment endpoints
    path('book/', BookAppointmentView.as_view(), name='book-appointment'), # The name convention is for the url path on the browser.
    path('my/', MyAppointmentsView.as_view(), name='my-appointments'),
    path('my/<int:appointment_id>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('my/<int:appointment_id>/cancel/', CancelAppointmentView.as_view(), name='cancel-appointment'),
]