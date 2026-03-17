import random
import string
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone


def generate_otp_code() -> str:
    return "".join(random.choices(string.digits, k=6))


class UserRole(models.TextChoices):
    PATIENT = "patient", "Patient"
    CAREGIVER = "caregiver", "Caregiver"
    PROVIDER = "provider", "Provider"
    ADMIN = "admin", "Admin"


class OTPPurpose(models.TextChoices):
    SIGNUP = "signup", "Signup"
    PASSWORD_RESET = "password_reset", "Password Reset"


class CompanyUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("is_email_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CompanyUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=150, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.PATIENT)
    is_email_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        null=True,
        blank=True,
    )
    city = models.CharField(max_length=100, null=True, blank=True)

    groups = models.ManyToManyField(
        "auth.Group",
        blank=True,
        related_name="health_mate_users",
        related_query_name="health_mate_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="health_mate_users",
        related_query_name="health_mate_user",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CompanyUserManager()

    class Meta:
        db_table = "company_users"
        ordering = ["-id"]

    def __str__(self):
        return self.email

    @property
    def display_name(self):
        if self.full_name:
            return self.full_name
        full = f"{self.first_name} {self.last_name}".strip()
        return full or self.email

    @property
    def profile_complete(self):
        """Returns True if user has completed all profile setup steps."""
        has_personal = bool(self.full_name and self.date_of_birth and self.gender)
        has_medical = hasattr(self, "medical_information")
        has_emergency = hasattr(self, "emergency_contact")
        return has_personal and has_medical and has_emergency


class OTPCode(models.Model):
    user = models.ForeignKey(CompanyUser, on_delete=models.CASCADE, related_name="otp_codes")
    purpose = models.CharField(max_length=32, choices=OTPPurpose.choices)
    code = models.CharField(max_length=6, default=generate_otp_code)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "otp_codes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email}::{self.purpose}"

    @classmethod
    def create_for_user(cls, user: CompanyUser, purpose: str, expiry_seconds: int = 600):
        return cls.objects.create(
            user=user,
            purpose=purpose,
            code=generate_otp_code(),
            expires_at=timezone.now() + timedelta(seconds=expiry_seconds),
        )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def verify(self, provided_code: str):
        if self.is_used:
            return False, "This code has already been used."
        if self.is_expired():
            return False, "OTP has expired. Request a new code."
        if self.attempts >= self.max_attempts:
            return False, "Too many failed attempts. Request a new code."
        if self.code != provided_code:
            self.attempts += 1
            self.save(update_fields=["attempts"])
            remaining = max(self.max_attempts - self.attempts, 0)
            return False, f"Invalid OTP. {remaining} attempts remaining."

        self.is_used = True
        self.verified_at = timezone.now()
        self.save(update_fields=["is_used", "verified_at"])
        return True, "OTP verified successfully."


# ── Desktop 9 — Medical Information ─────────────────────────────────────────

class MedicalInformation(models.Model):
    user = models.OneToOneField(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="medical_information"
    )
    chronic_medical_conditions = models.TextField(
        blank=True,
        default="",
        help_text="e.g. Diabetes, Hypertension, Asthma"
    )
    allergies_dietary_or_prescription = models.TextField(
        blank=True,
        default="",
        help_text="e.g. Penicillin, Peanuts, Gluten"
    )
    current_medication_history = models.TextField(
        blank=True,
        default="",
        help_text="e.g. Metformin 500mg daily"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_information"

    def __str__(self):
        return f"Medical info for {self.user.email}"


# ── Desktop 10 — Emergency Contact ──────────────────────────────────────────

class EmergencyContact(models.Model):
    user = models.OneToOneField(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name="emergency_contact"
    )
    name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    number_of_next_of_kin = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "emergency_contacts"

    def __str__(self):
        return f"Emergency contact for {self.user.email}"
    