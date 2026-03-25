from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import CompanyUser, OTPCode, OTPPurpose, UserRole


class AuthApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("accounts.serializers.verify_id_token")
    def test_register_rejects_non_patient_role(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"uid": "firebase-uid-1", "email": "new@user.com"}

        response = self.client.post(
            "/auth/register/",
            {
                "firebase_token": "dummy-token",
                "full_name": "New User",
                "role": UserRole.ADMIN,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])
        self.assertIn("role", response.data["data"])

    @patch("accounts.serializers.verify_id_token")
    def test_login_returns_access_and_refresh_tokens(self, mock_verify_id_token):
        mock_verify_id_token.return_value = {"uid": "firebase-uid-2", "email": "verified@user.com"}
        user = CompanyUser.objects.create_user(
            email="verified@user.com",
            firebase_uid="firebase-uid-2",
            full_name="Verified User",
            role=UserRole.PATIENT,
            is_active=True,
            is_email_verified=True,
        )

        response = self.client.post(
            "/auth/login/",
            {"firebase_token": "dummy-token"},
            format="json",
        )

       
        if response.status_code != 200:
            print("LOGIN RESPONSE", response.status_code, response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])
        self.assertIn("access", response.data["data"]["tokens"])
        self.assertIn("refresh", response.data["data"]["tokens"])
        self.assertEqual(response.data["data"]["user"]["email"], user.email)

    def test_validate_firebase_token_rejects_non_string(self):
        """Guard clauses ensure we never send a non-str value to the SDK."""
        from .serializers import FirebaseTokenMixin
        from rest_framework import serializers as drf_serializers

        mixin = FirebaseTokenMixin()
        with self.assertRaises(drf_serializers.ValidationError):
            mixin.validate_firebase_token(slice(None, 30, None))

    def test_verify_id_token_non_string_raises(self):
        """Low‑level helper should detect bad argument types before calling
        Firebase APIs; this prevents downstream ``unhashable type`` errors.
        """
        from .firebase import verify_id_token

        with self.assertRaises(ValueError):
            verify_id_token(slice(None, 30, None))

    @patch("accounts.views.update_user_password")
    def test_reset_password_confirm_updates_firebase_and_local_password(self, mock_update_password):
        user = CompanyUser.objects.create_user(
            email="reset@user.com",
            firebase_uid="firebase-uid-3",
            is_active=True,
            is_email_verified=True,
        )
        OTPCode.objects.create(
            user=user,
            purpose=OTPPurpose.PASSWORD_RESET,
            code="123456",
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        response = self.client.post(
            "/auth/reset-password/",
            {
                "action": "confirm",
                "email": user.email,
                "otp_code": "123456",
                "new_password": "StrongNewPass123!",
            },
            format="json",
        )

        user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertTrue(user.check_password("StrongNewPass123!"))
        mock_update_password.assert_called_once_with("firebase-uid-3", "StrongNewPass123!")

    @patch("accounts.views.send_a_mail.delay")
    def test_resend_otp_signup_sends_new_otp(self, mock_send_email_delay):
        user = CompanyUser.objects.create_user(
            email="signup@user.com",
            is_active=True,
            is_email_verified=False,
        )

        response = self.client.post(
            "/auth/resend-otp/",
            {
                "email": user.email,
                "purpose": OTPPurpose.SIGNUP,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertTrue(
            OTPCode.objects.filter(user=user, purpose=OTPPurpose.SIGNUP, is_used=False).exists()
        )
        mock_send_email_delay.assert_called_once()

    @patch("accounts.views.send_a_mail.delay")
    def test_resend_otp_signup_rejects_verified_email(self, mock_send_email_delay):
        user = CompanyUser.objects.create_user(
            email="verified-signup@user.com",
            is_active=True,
            is_email_verified=True,
        )

        response = self.client.post(
            "/auth/resend-otp/",
            {
                "email": user.email,
                "purpose": OTPPurpose.SIGNUP,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "Email is already verified.")
        mock_send_email_delay.assert_not_called()
