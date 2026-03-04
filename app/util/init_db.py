from app.core.database import Base, engine
from app.db.models.models import User, Provider, Availability, Appointment

def create_tables():
    Base.metadata.create_all(bind=engine)
    
print("✅ Tables Successfully Created")