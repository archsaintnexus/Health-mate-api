from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from .base import BaseRepository
from db.models.models import Provider, Availability, Appointment


class ProviderRepository(BaseRepository):

    def get_all_providers(self, specialty: str = None, location: str = None):
        query = self.session.query(Provider).filter(Provider.is_active == True)
        
        if specialty:
            query = query.filter(Provider.specialty.ilike(f"%{specialty}%")) # The "ilike" is used to check for specialty in Upper, Lower and Title case for the keywords. The "%" is used to search for any part of the keyword with the providers.
        
        if location:
            query = query.filter(Provider.location.ilike(f"%{location}%"))
        
        return query.all()

    def get_provider_by_id(self, provider_id: int):
        return self.session.query(Provider).filter_by(id=provider_id).first()



# This is used to get available specialists.
class AvailabilityRepository(BaseRepository):

    def get_slots_by_provider(self, provider_id: int):
        return (
            self.session.query(Availability)
            .filter_by(provider_id=provider_id, is_booked=False)
            .all()
        )

    def get_slot_by_id(self, slot_id: int):
        return self.session.query(Availability).filter_by(id=slot_id).first()



# This allows them to be able to book appointments.

class AppointmentRepository(BaseRepository):

    def create_appointment(self, user_id: int, data):
        slot = (
            self.session.query(Availability)
            .filter_by(id=data.slot_id)
            .with_for_update()
            .first()
        )

        if not slot:
            return None, "Slot not found"
        
        if slot.is_booked:
            return None, "Slot is already booked"

        try:
            slot.is_booked = True
            appointment = Appointment(
                user_id=user_id,
                provider_id=data.provider_id,
                slot_id=data.slot_id,
                reason=data.reason,
                notes=data.notes,
            )
            self.session.add(appointment)
            self.session.commit()
            self.session.refresh(appointment)

            # This Reloads with relationships before session closes
            return self.session.query(Appointment)\
                .options(joinedload(Appointment.provider), joinedload(Appointment.slot))\
                .filter_by(id=appointment.id).first(), None

        except IntegrityError:
            self.session.rollback()
            return None, "Slot is already booked"

    def get_user_appointments(self, user_id: int):
        return (
            self.session.query(Appointment)
            .options(joinedload(Appointment.provider), joinedload(Appointment.slot))
            .filter_by(user_id=user_id)
            .all()
        )

    def get_appointment_by_id(self, appointment_id: int, user_id: int):
        return (
            self.session.query(Appointment)
            .options(joinedload(Appointment.provider), joinedload(Appointment.slot))
            .filter_by(id=appointment_id, user_id=user_id)
            .first()
        )

    def cancel_appointment(self, appointment_id: int, user_id: int):
        appointment = self.get_appointment_by_id(appointment_id, user_id)
        if not appointment:
            return None
        
        appointment.status = "cancelled"
        appointment.slot.is_booked = False
        self.session.commit()
        self.session.refresh(appointment)

        return self.session.query(Appointment)\
            .options(joinedload(Appointment.provider), joinedload(Appointment.slot))\
            .filter_by(id=appointment.id).first()