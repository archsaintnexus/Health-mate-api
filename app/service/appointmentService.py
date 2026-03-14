from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
from db.repository.appointmentRepo import (
    ProviderRepository,
    AvailabilityRepository,
    AppointmentRepository
)
from db.schema.appointment import AppointmentCreate


class AppointmentService:
    def __init__(self, session: Session):
        self.__providerRepo     = ProviderRepository(session=session)
        self.__availabilityRepo = AvailabilityRepository(session=session)
        self.__appointmentRepo  = AppointmentRepository(session=session)

    # PROVIDERS 

    def search_providers(self, specialty: str = None, location: str = None):
        providers = self.__providerRepo.get_all_providers(
            specialty=specialty,
            location=location
        )
        if not providers:
            raise HTTPException(status_code=404, detail="No providers found")
        return providers

    def get_provider(self, provider_id: int):
        provider = self.__providerRepo.get_provider_by_id(provider_id=provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        return provider

    # AVAILABILITY 

    def get_provider_slots(self, provider_id: int):
        # This Confirm provider exists first, before assigning a slot to other patients.
        self.get_provider(provider_id=provider_id)

        slots = self.__availabilityRepo.get_slots_by_provider(provider_id=provider_id)
        if not slots:
            raise HTTPException(
                status_code=404,
                detail="No available slots for this provider"
            )
        return slots

    # APPOINTMENTS 

    def book_appointment(
        self,
        user_id: int,
        data: AppointmentCreate,
        background_tasks: BackgroundTasks
    ):
        # Confirm provider exists
        self.get_provider(provider_id=data.provider_id)

        appointment, error = self.__appointmentRepo.create_appointment(
            user_id=user_id,
            data=data
        )

        if error:
            raise HTTPException(status_code=409, detail=error)

        # Fire notification in background after booking succeeds
        background_tasks.add_task(
            send_booking_notification,
            appointment_id=appointment.id,
            user_id=user_id,
            provider_name=appointment.provider.full_name,
            start_time=str(appointment.slot.start_time)
        )

        return appointment

    def get_my_appointments(self, user_id: int):
        appointments = self.__appointmentRepo.get_user_appointments(user_id=user_id)
        return appointments

    def get_appointment(self, appointment_id: int, user_id: int):
        appointment = self.__appointmentRepo.get_appointment_by_id(
            appointment_id=appointment_id,
            user_id=user_id
        )
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment

    def cancel_appointment(self, appointment_id: int, user_id: int):
        appointment = self.__appointmentRepo.cancel_appointment(
            appointment_id=appointment_id,
            user_id=user_id
        )
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment


# NOTIFICATION HELPER 
# This runs in the background after booking - doesn't block the response

def send_booking_notification(
    appointment_id: int,
    user_id: int,
    provider_name: str,
    start_time: str
):
    # For now this just prints I'll replace this with
    # real email sending (fastapi-mail) when it's created.
    print(f"""
    ── BOOKING CONFIRMED ──
    Appointment ID : {appointment_id}
    User ID        : {user_id}
    Doctor         : {provider_name}
    Time           : {start_time}
    ──────────────────────
    """)