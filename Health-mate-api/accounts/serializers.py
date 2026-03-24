import logging # ADD THIS LINE
import os

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .firebase import verify_id_token
from .models import CompanyUser, EmergencyContact, MedicalInformation, OTPPurpose, UserRole


logger = logging.getLogger(__name__) 


class FirebaseTokenMixin:
    def validate_firebase_token(self, token):
        # --- DEBUG LOGS START ---
        logger.debug(f"FirebaseTokenMixin.validate_firebase_token: START")
        logger.debug(f"FirebaseTokenMixin.validate_firebase_token: Received token: '{token}'")
        logger.debug(f"FirebaseTokenMixin.validate_firebase_token: Type of received token: {type(token)}")
        # --- DEBUG LOGS END ---

        if not isinstance(token, str):
            # --- DEBUG LOGS START ---
            logger.error(f"FirebaseTokenMixin.validate_firebase_token: FAILED - Token is not a string!")
            logger.error(f"FirebaseTokenMixin.validate_firebase_token: Actual type: {type(token)}, Actual value: '{token}'")
            # --- DEBUG LOGS END ---
            raise serializers.ValidationError("firebase_token must be a string.")

        try:
            decoded = verify_id_token(token)
            logger.debug(f"FirebaseTokenMixin.validate_firebase_token: Token successfully decoded by Firebase.")
        except Exception as e:
            logger.error(f"FirebaseTokenMixin.validate_firebase_token: Error during Firebase token verification: {e}")
            raise serializers.ValidationError("Invalid or expired Firebase token.")

        uid = decoded.get("uid") or decoded.get("localId")
        email = decoded.get("email")
        if not uid or not email:
            logger.error(f"FirebaseTokenMixin.validate_firebase_token: Decoded token missing UID or Email claims. UID: {uid}, Email: {email}")
            raise serializers.ValidationError(
                "Firebase token must contain uid and email claims."
            )
        logger.debug(f"FirebaseTokenMixin.validate_firebase_token: Token valid and contains UID/Email. Decoded UID: {uid}, Email: {email}")
        logger.debug(f"FirebaseTokenMixin.validate_firebase_token: END - Returning decoded user.")
        return decoded


class RegisterSerializer(serializers.Serializer, FirebaseTokenMixin):
    firebase_token = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=["male", "female", "other"],
        required=False,
        allow_null=True,
        allow_blank=True
    )
    city = serializers.CharField(required=False, allow_blank=True, max_length=100)
    role = serializers.ChoiceField(
        choices=UserRole.choices,
        required=False,
        default=UserRole.PATIENT
    )

    def validate(self, attrs):
        logger.debug(f"RegisterSerializer.validate: START - attrs: {attrs}")
        requested_role = attrs.get("role", UserRole.PATIENT)
        if requested_role != UserRole.PATIENT:
            raise serializers.ValidationError({"role": "Public registration only allows patient role."})
        
        raw_firebase_token = attrs.get("firebase_token")
        logger.debug(f"RegisterSerializer.validate: Extracted firebase_token: '{raw_firebase_token}', Type: {type(raw_firebase_token)}")

        try:
            decoded_firebase_user = self.validate_firebase_token(raw_firebase_token)
        except serializers.ValidationError as e:
            logger.error(f"RegisterSerializer.validate: Caught ValidationError from firebase_token validation: {e.detail}")
            raise e
        except Exception as e:
            logger.exception("RegisterSerializer.validate: Unexpected error during Firebase token validation for registration.") # Uses logger.exception for traceback
            raise serializers.ValidationError("An internal server error occurred during Firebase authentication for registration.")

        attrs["firebase_user"] = decoded_firebase_user
        attrs.pop("firebase_token", None) 
        logger.debug(f"RegisterSerializer.validate: END - Validation successful.")
        return attrs


class LoginSerializer(serializers.Serializer, FirebaseTokenMixin):
    firebase_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # --- DEBUG LOGS START ---
        logger.debug(f"LoginSerializer.validate: START - attrs received: {attrs}")

        raw_firebase_token = attrs.get("firebase_token")

        # --- DEBUG LOGS START ---
        logger.debug(f"LoginSerializer.validate: Extracted raw_firebase_token: '{raw_firebase_token}'")
        logger.debug(f"LoginSerializer.validate: Type of raw_firebase_token: {type(raw_firebase_token)}")
        # --- DEBUG LOGS END ---
     
        try:
            decoded_firebase_user = self.validate_firebase_token(raw_firebase_token)
        except serializers.ValidationError as e:
            # --- DEBUG LOGS START ---
            logger.error(f"LoginSerializer.validate: Caught ValidationError from firebase_token validation: {e.detail}")
            # --- DEBUG LOGS END ---
            raise e
        except Exception as e:
            # --- DEBUG LOGS START ---
            logger.exception("LoginSerializer.validate: Unexpected error during Firebase token validation for login.") # Uses logger.exception for traceback
            # --- DEBUG LOGS END ---
            raise serializers.ValidationError("An internal server error occurred during Firebase authentication.")

        attrs["firebase_user"] = decoded_firebase_user
        attrs.pop("firebase_token", None)

        # --- DEBUG LOGS START ---
        logger.debug(f"LoginSerializer.validate: END - Validation successful. Final attrs: {attrs}")
        # --- DEBUG LOGS END ---
        return attrs


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.RegexField(regex=r"^\d{6}$")
    purpose = serializers.ChoiceField(
        choices=OTPPurpose.choices,
        default=OTPPurpose.SIGNUP,
        required=False
    )


class ResetPasswordSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["request", "confirm"])
    email = serializers.EmailField()
    otp_code = serializers.RegexField(regex=r"^\d{6}$", required=False)
    new_password = serializers.CharField(
        required=False,
        write_only=True,
        validators=[validate_password]
    )

    def validate(self, attrs):
        action = attrs["action"]
        if action == "confirm":
            if not attrs.get("otp_code"):
                raise serializers.ValidationError({"otp_code": "otp_code is required for confirm action."})
            if not attrs.get("new_password"):
                raise serializers.ValidationError({"new_password": "new_password is required for confirm action."})
        return attrs

class PersonalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = [
            "full_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "city",
        ]

    def validate_date_of_birth(self, value):
        from datetime import date
        if value and value >= date.today():
            raise serializers.ValidationError("Date of birth must be in the past.")
        return value

class MedicalInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInformation
        fields = [
            "id",
            "chronic_medical_conditions",
            "allergies_dietary_or_prescription",
            "current_medication_history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "name",
            "relationship",
            "phone_number",
            "number_of_next_of_kin",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    medical_information = MedicalInformationSerializer(read_only=True)
    emergency_contact = EmergencyContactSerializer(read_only=True)
    profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = CompanyUser
        fields = [
            "id",
            "email",
            "firebase_uid",
            "full_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "city",
            "role",
            "is_email_verified",
            "profile_complete",
            "medical_information",
            "emergency_contact",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "email", "firebase_uid",
            "is_email_verified", "created_at", "updated_at"
        ]
