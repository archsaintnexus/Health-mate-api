from django.db import migrations, models
import django.utils.timezone

import accounts.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompanyUser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("firebase_uid", models.CharField(blank=True, max_length=128, null=True, unique=True)),
                ("full_name", models.CharField(blank=True, default="", max_length=150)),
                ("phone_number", models.CharField(blank=True, default="", max_length=20)),
                ("role", models.CharField(choices=[("patient", "Patient"), ("caregiver", "Caregiver"), ("provider", "Provider"), ("admin", "Admin")], default="patient", max_length=20)),
                ("is_email_verified", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        related_name="health_mate_users",
                        related_query_name="health_mate_user",
                        to="auth.group",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="health_mate_users",
                        related_query_name="health_mate_user",
                        to="auth.permission",
                    ),
                ),
            ],
            options={
                "db_table": "company_users",
                "ordering": ["-id"],
            },
            managers=[
                ("objects", accounts.models.CompanyUserManager()),
            ],
        ),
        migrations.CreateModel(
            name="OTPCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("purpose", models.CharField(choices=[("signup", "Signup"), ("password_reset", "Password Reset")], max_length=32)),
                ("code", models.CharField(default=accounts.models.generate_otp_code, max_length=6)),
                ("is_used", models.BooleanField(default=False)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("max_attempts", models.PositiveIntegerField(default=5)),
                ("expires_at", models.DateTimeField()),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="otp_codes", to="accounts.companyuser"),
                ),
            ],
            options={
                "db_table": "otp_codes",
                "ordering": ["-created_at"],
            },
        ),
    ]
