import os

from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from helper.response import CustomResponse
from helper.tasks import send_a_mail

from .firebase import update_user_password
from .models import CompanyUser, EmergencyContact, MedicalInformation, OTPCode, OTPPurpose, UserRole
from .serializers import (
    EmergencyContactSerializer,
    LoginSerializer,
    MedicalInformationSerializer,
    PersonalInformationSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserProfileSerializer,
    VerifyOtpSerializer,
)


def _otp_expiry_seconds():
    return int(os.getenv("OTP_EXPIRY_SECONDS", "600"))


def _send_email(subject: str, html_message: str, recipient: str):
    send_a_mail(
        title=subject,
        message=html_message,
        to=recipient,
        is_html=True,
    )


def _build_otp_email(display_name: str, code: str, reason: str):
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h3>{reason}</h3>
        <p>Hello {display_name},</p>
        <p>Your one-time code is:</p>
        <h2 style="letter-spacing: 3px;">{code}</h2>
        <p>This code expires in {_otp_expiry_seconds() // 60} minutes.</p>
      </body>
    </html>
    """

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="Registration successful. OTP sent to email."),
            400: OpenApiResponse(description="Validation error"),
            409: OpenApiResponse(description="User already exists"),
        },
        description="Register a new Health Mate user. A Firebase ID token is required. An OTP will be sent to the provided email for verification.",
        tags=["Authentication"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        firebase_user = serializer.validated_data["firebase_user"]
        firebase_uid = firebase_user.get("uid") or firebase_user.get("localId")
        email = firebase_user.get("email")

        existing_user = CompanyUser.objects.filter(email=email).first()
        if existing_user:
            if not existing_user.firebase_uid:
                existing_user.firebase_uid = firebase_uid
                existing_user.save(update_fields=["firebase_uid"])
            return CustomResponse(False, "User already exists. Please log in.", 409)

        user = CompanyUser.objects.create_user(
            email=email,
            firebase_uid=firebase_uid,
            full_name=serializer.validated_data.get("full_name", ""),
            phone_number=serializer.validated_data.get("phone_number", ""),
            date_of_birth=serializer.validated_data.get("date_of_birth"),
            gender=serializer.validated_data.get("gender"),
            city=serializer.validated_data.get("city"),
            role=UserRole.PATIENT,
            is_active=True,
            is_email_verified=False,
        )

        otp = OTPCode.create_for_user(
            user=user,
            purpose=OTPPurpose.SIGNUP,
            expiry_seconds=_otp_expiry_seconds(),
        )

        _send_email(
            subject="Welcome to Health Mate",
            html_message=_build_otp_email(
                user.display_name,
                otp.code,
                "Verify your Health Mate account"
            ),
            recipient=user.email,
        )

        return CustomResponse(
            True,
            "Registration successful. OTP sent to email.",
            201,
            {
                "email": user.email,
                "verification_required": True,
                "user": {
                    "full_name": user.full_name,
                    "email": user.email,
                    "gender": user.gender,
                    "city": user.city,
                    "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None,
                }
            },
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful. JWT tokens returned."),
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Firebase account mismatch"),
            403: OpenApiResponse(description="Email not verified"),
            404: OpenApiResponse(description="No account found"),
        },
        description="Login using a Firebase ID token. Returns JWT access and refresh tokens.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        firebase_user = serializer.validated_data["firebase_user"]
        firebase_uid = firebase_user.get("uid") or firebase_user.get("localId")
        email = firebase_user.get("email")

        user = CompanyUser.objects.filter(email=email).first()
        if not user:
            return CustomResponse(False, "No account found. Please register first.", 404)

        if not user.firebase_uid:
            user.firebase_uid = firebase_uid
            user.save(update_fields=["firebase_uid"])
        elif user.firebase_uid != firebase_uid:
            return CustomResponse(False, "Firebase account mismatch for this email.", 401)

        if not user.is_email_verified:
            return CustomResponse(False, "Email not verified. Please verify OTP first.", 403)

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        refresh["email"] = user.email
        access = refresh.access_token
        access["role"] = user.role
        access["email"] = user.email

        return CustomResponse(
            True,
            "Login successful.",
            200,
            {
                "tokens": {"access": str(access), "refresh": str(refresh)},
                "user": UserProfileSerializer(user).data,
            },
        )


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyOtpSerializer,
        responses={
            200: OpenApiResponse(description="OTP verified successfully."),
            400: OpenApiResponse(description="Invalid or expired OTP"),
            404: OpenApiResponse(description="User not found"),
        },
        description="Verify an OTP code for email verification or password reset. Purpose can be 'signup' or 'password_reset'.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["otp_code"]
        purpose = serializer.validated_data["purpose"]

        user = CompanyUser.objects.filter(email=email).first()
        if not user:
            return CustomResponse(False, "User not found.", 404)

        otp = (
            OTPCode.objects.filter(user=user, purpose=purpose, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if not otp:
            return CustomResponse(False, "No active OTP found. Request a new one.", 400)

        is_valid, message = otp.verify(code)
        if not is_valid:
            return CustomResponse(False, message, 400)

        if purpose == OTPPurpose.SIGNUP:
            user.is_email_verified = True
            user.is_active = True
            user.save(update_fields=["is_email_verified", "is_active"])

        return CustomResponse(True, message, 200)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(description="OTP sent or password reset successfully."),
            400: OpenApiResponse(description="Invalid OTP or validation error"),
            502: OpenApiResponse(description="Firebase password update failed"),
        },
        description=(
            "Two-step password reset. "
            "Step 1: Send action='request' with email to receive OTP. "
            "Step 2: Send action='confirm' with email, otp_code and new_password to reset."
        ),
        tags=["Authentication"],
    )
    @transaction.atomic
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        action = serializer.validated_data["action"]
        email = serializer.validated_data["email"]

        user = CompanyUser.objects.filter(email=email).first()

        if action == "request":
            if user and user.is_active:
                otp = OTPCode.create_for_user(
                    user=user,
                    purpose=OTPPurpose.PASSWORD_RESET,
                    expiry_seconds=_otp_expiry_seconds(),
                )
                _send_email(
                    subject="Health Mate Password Reset OTP",
                    html_message=_build_otp_email(
                        user.display_name,
                        otp.code,
                        "Use this OTP to reset your password",
                    ),
                    recipient=user.email,
                )
            return CustomResponse(
                True,
                "If an account with this email exists, a reset OTP has been sent.",
                200,
            )

        if not user:
            return CustomResponse(False, "Invalid email or OTP.", 400)

        otp_code = serializer.validated_data["otp_code"]
        new_password = serializer.validated_data["new_password"]

        otp = (
            OTPCode.objects.filter(user=user, purpose=OTPPurpose.PASSWORD_RESET, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if not otp:
            return CustomResponse(False, "No active reset OTP found.", 400)

        is_valid, message = otp.verify(otp_code)
        if not is_valid:
            return CustomResponse(False, message, 400)

        if user.firebase_uid:
            try:
                update_user_password(user.firebase_uid, new_password)
            except ValueError:
                return CustomResponse(False, "Unable to reset password at this time.", 502)

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return CustomResponse(
            True,
            "Password reset successful. You can now log in with your new password.",
            200,
        )


# ── Profile Setup Views ──────────────────────────────────────────────────────

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: UserProfileSerializer,
            404: OpenApiResponse(description="User not found"),
        },
        description="Get the complete profile of the currently authenticated user including medical info and emergency contact.",
        tags=["Profile"],
    )
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return CustomResponse(
            True,
            "Profile retrieved successfully.",
            200,
            serializer.data,
        )


class PersonalInformationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PersonalInformationSerializer,
        responses={
            200: PersonalInformationSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        description="Update personal information — Desktop 8 in Figma. Requires JWT authentication.",
        tags=["Profile"],
    )
    def patch(self, request):
        user = request.user
        serializer = PersonalInformationSerializer(
            user,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        serializer.save()

        return CustomResponse(
            True,
            "Personal information updated successfully.",
            200,
            serializer.data,
        )


class MedicalInformationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=MedicalInformationSerializer,
        responses={
            200: MedicalInformationSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        description="Create or update medical information — Desktop 9 in Figma. Requires JWT authentication.",
        tags=["Profile"],
    )
    def post(self, request):
        user = request.user

        medical_info, created = MedicalInformation.objects.get_or_create(user=user)
        serializer = MedicalInformationSerializer(
            medical_info,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        serializer.save()

        message = "Medical information saved successfully."
        return CustomResponse(True, message, 200, serializer.data)


class EmergencyContactView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EmergencyContactSerializer,
        responses={
            200: EmergencyContactSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        description="Create or update emergency contact — Desktop 10 in Figma. Requires JWT authentication.",
        tags=["Profile"],
    )
    def post(self, request):
        user = request.user

        emergency_contact, created = EmergencyContact.objects.get_or_create(user=user)
        serializer = EmergencyContactSerializer(
            emergency_contact,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return CustomResponse(False, "Validation error", 400, serializer.errors)

        serializer.save()

        message = "Emergency contact saved successfully."
        return CustomResponse(True, message, 200, serializer.data)
    