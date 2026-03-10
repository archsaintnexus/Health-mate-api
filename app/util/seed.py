from app.core.database import SessionLocal
from app.db.models.models import Provider, Availability
from datetime import datetime, timedelta


def seed_providers():
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Provider).first()
        if existing:
            print("Database already seeded — skipping.")
            return

        # ── PROVIDERS ─────────────────────────────────────────────
        providers = [
            Provider(
                full_name="Dr. Amina Bello",
                specialty="Cardiology",
                location="Lagos Island, Lagos",
                bio="Specialist in cardiovascular diseases with over 10 years of experience at LUTH.",
                avatar_url="https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop",
                rating=4.8,
                years_exp=10,
                is_active=True
            ),
            Provider(
                full_name="Dr. Chukwuemeka Okafor",
                specialty="General Practice",
                location="Victoria Island, Lagos",
                bio="Family physician providing comprehensive primary care for all ages.",
                avatar_url="https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=400&h=400&fit=crop",
                rating=4.6,
                years_exp=7,
                is_active=True
            ),
            Provider(
                full_name="Dr. Fatima Aliyu",
                specialty="Pediatrics",
                location="Abuja, FCT",
                bio="Dedicated to providing quality healthcare for infants, children and adolescents.",
                avatar_url="https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=400&h=400&fit=crop",
                rating=4.9,
                years_exp=12,
                is_active=True
            ),
            Provider(
                full_name="Dr. Tunde Adeyemi",
                specialty="Orthopedics",
                location="Ikeja, Lagos",
                bio="Specialist in bone and joint conditions, sports injuries and rehabilitation.",
                avatar_url="https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=400&h=400&fit=crop",
                rating=4.7,
                years_exp=9,
                is_active=True
            ),
            Provider(
                full_name="Dr. Ngozi Eze",
                specialty="Dermatology",
                location="Port Harcourt, Rivers",
                bio="Expert in skin conditions, cosmetic dermatology and hair disorders.",
                avatar_url="https://images.unsplash.com/photo-1651008376811-b90baee60c1f?w=400&h=400&fit=crop",
                rating=4.5,
                years_exp=8,
                is_active=True
            ),
            Provider(
                full_name="Dr. Ibrahim Musa",
                specialty="Neurology",
                location="Kano, Kano State",
                bio="Neurologist specialising in headaches, epilepsy and stroke management.",
                avatar_url="https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&h=400&fit=crop",
                rating=4.7,
                years_exp=11,
                is_active=True
            ),
        ]

        db.add_all(providers)
        db.commit()

        # Refresh to get IDs
        for provider in providers:
            db.refresh(provider)

        print(f"✅ {len(providers)} providers seeded.")

        # ── AVAILABILITY SLOTS ────────────────────────────────────
        # Generate slots for the next 7 days
        # Each provider gets morning and afternoon slots each day

        slots = []
        now = datetime.utcnow()

        for provider in providers:
            for day_offset in range(1, 8):  # next 7 days
                base_date = now + timedelta(days=day_offset)

                # Morning slots — 9am, 10am, 11am
                for hour in [9, 10, 11]:
                    start = base_date.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                    slots.append(Availability(
                        provider_id=provider.id,
                        start_time=start,
                        end_time=start + timedelta(minutes=30),
                        is_booked=False
                    ))

                # Afternoon slots — 2pm, 3pm, 4pm
                for hour in [14, 15, 16]:
                    start = base_date.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                    slots.append(Availability(
                        provider_id=provider.id,
                        start_time=start,
                        end_time=start + timedelta(minutes=30),
                        is_booked=False
                    ))

        db.add_all(slots)
        db.commit()

        total_slots = len(slots)
        print(f"✅ {total_slots} availability slots seeded.")
        print("\nSeed complete. You can now test the appointments flow.")
        print("\nProviders seeded:")
        for p in providers:
            print(f"  - {p.full_name} | {p.specialty} | {p.location}")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_providers()