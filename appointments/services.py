from datetime import datetime, timedelta
from .models import DoctorAvailability, Appointment, AppointmentStatus
from consultation.models import DoctorProfile


class AppointmentService:

    @staticmethod
    def get_available_slots(doctor: DoctorProfile, date: datetime.date) -> list:
        """
        Get available time slots for a doctor on a given date.
        """
        day_of_week = date.weekday()

        # Get doctor's availability for this day
        availability = DoctorAvailability.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_available=True
        ).first()

        if not availability:
            return []

        # Generate all slots
        slots = []
        current_time = datetime.combine(date, availability.start_time)
        end_time = datetime.combine(date, availability.end_time)
        slot_duration = timedelta(minutes=availability.slot_duration_minutes)

        while current_time + slot_duration <= end_time:
            slots.append(current_time.time())
            current_time += slot_duration

        # Remove already booked slots
        booked_times = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date,
            status__in=[
                AppointmentStatus.PENDING,
                AppointmentStatus.CONFIRMED
            ]
        ).values_list("appointment_time", flat=True)

        available_slots = [
            slot for slot in slots
            if slot not in booked_times
        ]

        return available_slots
    