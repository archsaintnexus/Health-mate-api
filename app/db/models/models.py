from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False) # The "String(50)" allows to restrict the length of the first name to 50 characters.
    last_name = Column(String(100), nullable=False) 
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number=Column(String(11), index=True, nullable=True)
    address = Column(String, nullable=True)
    password = Column(String(250), nullable=False) # Restriction is set to 250 characters to accommodate hashed passwords, which can be longer than plain text passwords.
    created_at = Column(DateTime, default=datetime.utcnow)
    appointments = relationship("Appointment", back_populates="user")




# The Provider model represents the Doctor or Healthcare professional
class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True) # Id is always required
    full_name = Column(String(150), nullable=False)
    specialty = Column(String(150), nullable=False, index=True) # Their area of specialization
    location = Column(String(150), nullable=False, index=True) # Where they are based.
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(300), nullable=True)
    rating = Column(Float, default=0.0) # Rating is always in decimal
    years_exp = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    availability = relationship("Availability", back_populates="provider")
    appointments = relationship("Appointment", back_populates="provider")




# This allows us to know each specialist schedule.
class Availability(Base):
    __tablename__ = "availability"

    id          = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    start_time  = Column(DateTime, nullable=False)
    end_time    = Column(DateTime, nullable=False)
    is_booked   = Column(Boolean, default=False, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    provider    = relationship("Provider", back_populates="availability")
    appointment = relationship("Appointment", back_populates="slot", uselist=False)

    __table_args__ = (
        UniqueConstraint("provider_id", "start_time", name="uq_provider_slot"), # The UniqueConstraint here is used to  monitor concurrency and ensure when appointments are booked they are only booked by one person at a time.
    )




# This shows the appointments each user has with the Doctors or Healthcare providers.
class Appointment(Base):
    __tablename__ = "appointments"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    slot_id     = Column(Integer, ForeignKey("availability.id"), nullable=False, unique=True) # If the Specialist is available we get to know if they can be requested for an appointment.
    reason      = Column(String(500), nullable=True)
    notes       = Column(Text, nullable=True)
    status      = Column(String(20), default="confirmed")
    created_at  = Column(DateTime, default=datetime.utcnow)

    user        = relationship("User", back_populates="appointments")
    provider    = relationship("Provider", back_populates="appointments")
    slot        = relationship("Availability", back_populates="appointment")