from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .firebase import verify_id_token
from .models import CompanyUser, OTPPurpose, UserRole


class FirebaseTokenMixin:
    def validate_firebase_token(self, token):

        if not isinstance(token, str):
            raise serializers.ValidationError("firebase_token must be a string.")

        try:
            decoded = verify_id_token(token)
        except Exception:
            raise serializers.ValidationError("Invalid or expired Firebase token.")

        uid = decoded.get("uid") or decoded.get("localId")
        email = decoded.get("email")
        if not uid or not email:
            raise serializers.ValidationError(
                "Firebase token must contain uid and email claims."
            )
        return decoded 


class RegisterSerializer(serializers.Serializer, FirebaseTokenMixin):
    firebase_token = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)
    role = serializers.ChoiceField(choices=UserRole.choices, required=False, default=UserRole.PATIENT)

    def validate(self, attrs):
        requested_role = attrs.get("role", UserRole.PATIENT)
        if requested_role != UserRole.PATIENT:
            raise serializers.ValidationError({"role": "Public registration only allows patient role."})

        attrs["firebase_user"] = attrs.pop("firebase_token")
        return attrs


class LoginSerializer(serializers.Serializer, FirebaseTokenMixin):
    firebase_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs["firebase_user"] = attrs.pop("firebase_token")
        return attrs


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.RegexField(regex=r"^\d{6}$")
    purpose = serializers.ChoiceField(choices=OTPPurpose.choices, default=OTPPurpose.SIGNUP, required=False)


class ResetPasswordSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["request", "confirm"])
    email = serializers.EmailField()
    otp_code = serializers.RegexField(regex=r"^\d{6}$", required=False)
    new_password = serializers.CharField(required=False, write_only=True, validators=[validate_password])

    def validate(self, attrs):
        action = attrs["action"]
        if action == "confirm":
            if not attrs.get("otp_code"):
                raise serializers.ValidationError({"otp_code": "otp_code is required for confirm action."})
            if not attrs.get("new_password"):
                raise serializers.ValidationError({"new_password": "new_password is required for confirm action."})
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = [
            "id",
            "email",
            "firebase_uid",
            "full_name",
            "phone_number",
            "role",
            "is_email_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "firebase_uid", "is_email_verified", "created_at", "updated_at"]
