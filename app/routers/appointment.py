from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.schema.appointment import (
    ProviderOutput,
    SlotOutput,
    AppointmentCreate,
    AppointmentOutput
)
from app.service.appointmentService import AppointmentService
from app.util.protectRoute import get_current_user
from app.db.schema.user import UserOutput
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

appointmentRouter = APIRouter()


# PROVIDER ENDPOINTS 

@appointmentRouter.get("/providers", response_model=List[ProviderOutput])
async def search_providers(
    specialty: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserOutput = Depends(get_current_user)
):
    return AppointmentService(session=db).search_providers(
        specialty=specialty,
        location=location
    )


@appointmentRouter.get("/providers/{provider_id}", response_model=ProviderOutput)
async def get_provider(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: UserOutput = Depends(get_current_user)
):
    return AppointmentService(session=db).get_provider(provider_id=provider_id)


# AVAILABILITY ENDPOINTS 

@appointmentRouter.get("/providers/{provider_id}/slots", response_model=List[SlotOutput])
async def get_provider_slots(
    provider_id: int,
    db: Session = Depends(get_db),
    current_user: UserOutput = Depends(get_current_user)
):
    return AppointmentService(session=db).get_provider_slots(provider_id=provider_id)


#  APPOINTMENT ENDPOINTS 

@appointmentRouter.post("/", status_code=201, response_model=AppointmentOutput)
async def book_appointment(
    data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserOutput = Depends(get_current_user)
):
    return AppointmentService(session=db).book_appointment(
        user_id=current_user.id,
        data=data,
        background_tasks=background_tasks
    )


@appointmentRouter.get("/", response_model=List[AppointmentOutput])
async def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: UserOutput = Depends(get_current_user)
):
    return AppointmentService(session=db).get_my_appointments(
        user_id=current_user.id
    )


@appointmentRouter.get("/{appointment_id}", response_model=AppointmentOutput)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: UserOutput = Depends(get_current_user)
):
    return AppointmentService(session=db).get_appointment(
        appointment_id=appointment_id,
        user_id=current_user.id
    )


@appointmentRouter.delete("/{appointment_id}", response_model=AppointmentOutput)
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: UserOutput = Depends(get_current_user)
):
    return AppointmentService(session=db).cancel_appointment(
        appointment_id=appointment_id,
        user_id=current_user.id
    )