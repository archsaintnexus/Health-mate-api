Health Mate API
A secure, production-ready healthcare platform API built with Django REST Framework, Firebase Authentication, PostgreSQL, Redis, Celery, and Docker.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Authentication Flow](#authentication-flow)
- [OTP Flow](#otp-flow)
- [Password Reset Flow](#password-reset-flow)
- [JWT Tokens](#jwt-tokens)
- [Role-Based Access](#role-based-access)
- [Email Service](#email-service)
- [Running Tests](#running-tests)
- [Docker Services](#docker-services)
- [Security Notes](#security-notes)
- [Additional Modules (Appointments/Consultation/Medicals/Pharmacy/Homecare)](#additional-modules-appointmentsconsultationmedicalspharmacyhomecare)
- [Troubleshooting](#troubleshooting)

---

## Overview
Health Mate connects patients with healthcare providers through a secure API-driven platform supporting appointment booking, video consultations, medical records management, lab test tracking, and pharmacy services.

### Key Features

- Firebase Authentication + Django JWT dual-token strategy
- OTP-based email verification with brute force protection
- Role-based access control (Patient, Provider, Admin, Caregiver)
- Video consultations via Daily.co
- Async email delivery via Celery + Resend
- Medical records with vital signs, prescriptions, and care plans
- Lab test booking and result tracking
- Appointment booking with doctor availability slots
- HIPAA-compliant data storage and transmission
---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Django | 4.2.28 | Web framework |
| Django REST Framework | 3.16.1 | REST API |
| djangorestframework-simplejwt | 5.3.1 | JWT authentication |
| firebase-admin | 6.5.0 | Firebase token verification |
| Celery | 5.3.6 | Async task queue |
| Redis | 7 | Message broker + cache |
| PostgreSQL | 15 | Primary database |
| django-celery-beat | 2.8.1 | Scheduled tasks |
| drf-spectacular | 0.28.0 | API documentation |
| Resend | — | Email delivery |
| Cloudinary | 1.44.1 | Media storage for pharmacy images |
| Docker | — | Containerisation |
|Daily.co |APILatestVideo |consultations|
|Gunicorn |23.0.0| |Production server|

---

## Project Structure

```text
django-structure/
├── core/                        # Django config
│   ├── settings.py
│   ├── celery.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                    # Authentication app
│   ├── models.py                # CompanyUser, OTPCode
│   ├── views.py                 # RegisterView, LoginView, etc.
│   ├── serializers.py           # Request/response serializers
│   ├── firebase.py              # Firebase Admin SDK helpers
│   └── urls.py                  # Auth URL routes
├── appointments/                # Appointment booking & schedules
├── consultation/                # Consultation flow + doctor profile
├── medicals/                    # Medical records, prescriptions, labs
├── pharmacy/                    # Pharmacy products & orders
├── homecare/                    # Homecare services & requests
├── helper/
│   ├── tasks.py                 # send_a_mail + periodic tasks
│   └── response.py              # CustomResponse helper
├── firebase-credentials.json    # Firebase service account (DO NOT COMMIT)
├── manage.py
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Docker Desktop
- Firebase Project
- Resend Account (for email delivery)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/health-mate-api.git
cd health-mate-api
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Add Firebase Credentials

Download your Firebase service account key:

```text
Firebase Console → Project Settings → Service Accounts
→ Generate new private key → Download JSON
→ Rename to: firebase-credentials.json
→ Place in: Health-mate-api/
```

### 4. Build and Start

```bash
docker-compose up --build
```

### 5. Run Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 6. Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 7. Visit the API

| URL | Description |
|---|---|
| http://localhost:8000/api/docs/ | Swagger UI |
| http://localhost:8000/admin/ | Django Admin |

---

SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=health_mate
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

FIREBASE_CREDENTIALS_PATH=/app/django-structure/firebase-credentials.json
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id

RESEND_API_KEY=re_xxxx
RESEND_FROM_EMAIL=noreply@yourdomain.com

DAILY_API_KEY=your-daily-api-key
DAILY_API_URL=https://api.daily.co/v1
DAILY_SUBDOMAIN=yourapp

JWT_ACCESS_TOKEN_LIFETIME=900
JWT_REFRESH_TOKEN_LIFETIME=604800
OTP_EXPIRY_SECONDS=600

CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
```

> ⚠️ Never commit `.env` or `firebase-credentials.json` to version control.

---

## API Endpoints

Base URL: `http://localhost:8000`

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/register/` | Register new user | No |
| POST | `/auth/login/` | Login with Firebase token | No |
| POST | `/auth/verify-otp/` | Verify OTP code | No |
| POST | `/auth/reset-password/` | Request or confirm password reset | No |

---

### POST `/auth/register/`

Register a new user. Requires a valid Firebase ID token.

**Request Body:**

```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIs...",
  "full_name": "John Doe",
  "phone_number": "+2348012345678",
  "role": "patient"
}
```

**Success Response (201):**

```json
{
  "success": true,
  "message": "Registration successful. OTP sent to email.",
  "data": {
    "email": "john@example.com",
    "verification_required": true
  }
}
```

**Error Responses:**

| Code | Reason |
|---|---|
| 400 | Validation error / Invalid Firebase token |
| 409 | User already exists |

---

### POST `/auth/login/`

Login using a Firebase ID token. Returns JWT tokens.

**Request Body:**

```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "tokens": {
      "access": "eyJhbGciOiJIUzI1NiIs...",
      "refresh": "eyJhbGciOiJIUzI1NiIs..."
    },
    "user": {
      "id": "uuid",
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "patient",
      "is_email_verified": true
    }
  }
}
```

**Error Responses:**

| Code | Reason |
|---|---|
| 400 | Validation error |
| 401 | Firebase account mismatch |
| 403 | Email not verified |
| 404 | Account not found |

---

### POST `/auth/verify-otp/`

Verify OTP for email verification after registration.

**Request Body:**

```json
{
  "email": "john@example.com",
  "otp_code": "123456",
  "purpose": "signup"
}
```

**Purpose Options:**

| Value | Use Case |
|---|---|
| `signup` | Email verification after registration |
| `password_reset` | Password reset verification |

**Success Response (200):**

```json
{
  "success": true,
  "message": "OTP verified successfully."
}
```

---

### POST `/auth/reset-password/`

Two-step password reset.

**Step 1 — Request OTP:**

```json
{
  "action": "request",
  "email": "john@example.com"
}
```

**Step 2 — Confirm Reset:**

```json
{
  "action": "confirm",
  "email": "john@example.com",
  "otp_code": "123456",
  "new_password": "NewSecurePass123!"
}
```

**Success Response (200):**

```json
{
  "success": true,
  "message": "Password reset successful. You can now log in with your new password."
}
```

---

## Authentication Flow

```text
CLIENT                          BACKEND                        FIREBASE
  │                               │                               │
  │── Sign in with Firebase ──────────────────────────────────── │
  │                               │                        Returns ID Token
  │                               │                               │
  │── POST /auth/register/ ──────►│                               │
  │   { firebase_token, ... }     │── verify_id_token() ─────────►│
  │                               │◄─ decoded claims ─────────────│
  │                               │                               │
  │                               │── Create Django User          │
  │                               │── Generate OTP                │
  │                               │── Send OTP Email (Celery)     │
  │◄─ 201 { email, tokens } ──────│                               │
  │                               │                               │
  │── POST /auth/verify-otp/ ────►│                               │
  │   { email, otp_code }         │── Validate OTP                │
  │◄─ 200 { verified } ───────────│                               │
  │                               │                               │
  │── POST /auth/login/ ─────────►│                               │
  │   { firebase_token }          │── verify_id_token() ─────────►│
  │                               │◄─ decoded claims ─────────────│
  │◄─ 200 { access, refresh } ────│                               │
```

---

## OTP Flow

- OTP codes are **6 digits** and expire in **10 minutes** (configurable via `OTP_EXPIRY_SECONDS`)
- Previous unused OTPs for the same user and purpose are invalidated when a new one is created
- OTPs are stored in PostgreSQL and verified server-side
- Emails are sent asynchronously via **Celery** using the **Resend API**

---

## Password Reset Flow

```text
1. POST /auth/reset-password/  { action: "request", email }
   → OTP sent to email (even if email doesn't exist, returns 200 to prevent enumeration)

2. Check email for 6-digit OTP code

3. POST /auth/reset-password/  { action: "confirm", email, otp_code, new_password }
   → Password updated in both Django and Firebase
   → All existing JWT tokens invalidated
```

---

## JWT Tokens

| Token | Lifetime | Purpose |
|---|---|---|
| Access Token | 15 minutes | Authenticate API requests |
| Refresh Token | 7 days | Get new access tokens |

### Using the Access Token

Include in every authenticated request:

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### JWT Claims

```json
{
  "user_id": "uuid",
  "email": "john@example.com",
  "role": "patient",
  "exp": 1234567890
}
```

### Token Rotation

- Refresh tokens rotate on every use
- Old refresh tokens are blacklisted automatically
- All tokens are invalidated on password reset

---

## Role-Based Access

| Role | Description |
|---|---|
| `patient` | Default role — book appointments, view records |
| `provider` | Healthcare provider — manage appointments |
| `admin` | Full system access |
| `family_member` | Book on behalf of dependents |

> Public registration only allows the `patient` role.

---

## Email Service

Emails are sent asynchronously using **Celery** and the **Resend API**.

### Celery Task

```python
send_a_mail.delay(
    title="Subject",
    message="<h1>HTML Body</h1>",
    to="user@example.com",
    is_html=True
)
```

### Monitor Tasks

Visit Flower at `http://localhost:5555` to monitor Celery tasks in real time.

---

## Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test accounts

# Run with verbosity
docker-compose exec web python manage.py test --verbosity=2
```

---

## Docker Services

| Service | Port | Description |
|---|---|---|
| `web` | 8000 | Django API server |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis broker + cache |
| `celery` | — | Celery worker |
| `celery-beat` | — | Scheduled task runner |

### Useful Commands

```bash
# Start all services
docker-compose up --build

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v

# View logs
docker-compose logs web
docker-compose logs celery

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Open Django shell
docker-compose exec web python manage.py shell
```

---

## Security Notes

- `firebase-credentials.json` must **never** be committed to Git
- `.env` file must **never** be committed to Git
- Firebase ID tokens expire in **1 hour** — get a fresh token when testing
- JWT access tokens expire in **15 minutes** in production
- Rate limiting is applied on login and password reset endpoints via Redis
- All passwords are validated against Django's built-in password validators
- HTTPS should be enforced in production (`SECURE_SSL_REDIRECT=True`)

---

## Additional Modules (Appointments/Consultation/Medicals/Pharmacy/Homecare)

In addition to authentication, this backend currently includes:

- **Appointments** endpoints under `/appointments/`
- **Consultation** endpoints under `/consultations/`
- **Medicals** endpoints under `/medicals/`
- **Pharmacy** endpoints under `/api/pharmacy/`
- **Homecare** endpoints under `/api/homecare/`

Swagger docs: `http://localhost:8000/api/docs/`

---

## Troubleshooting

### Cloudinary module error

If you see:

```text
ModuleNotFoundError: No module named 'cloudinary'
```

Make sure:

- `cloudinary==1.44.1` exists in `requirements.txt`
- `'cloudinary'` is in `INSTALLED_APPS`

Then rebuild:

```bash
docker-compose down
docker-compose up --build
```

### Pharmacy / Homecare not visible on localhost

Use these base routes:

- `http://localhost:8000/api/pharmacy/`
- `http://localhost:8000/api/homecare/`

They are not mounted at `/pharmacy/` or `/homecare/`.

---

## .gitignore Essentials

```gitignore
.env
firebase-credentials.json
get_token.ps1
__pycache__/
*.pyc
venv/
db.sqlite3
```
