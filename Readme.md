# Health Mate API

> A secure, production-ready healthcare platform API built with Django REST Framework, Firebase Authentication, PostgreSQL (Supabase), Redis (Upstash), Celery, Cloudinary, and Docker.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16-red)](https://www.django-rest-framework.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [System Architecture](#system-architecture)
4. [System Design](#system-design)
5. [Database Design](#database-design)
6. [Entity Relationship Diagram (ERD)](#entity-relationship-diagram-erd)
7. [Project Structure](#project-structure)
8. [API Modules](#api-modules)
9. [Authentication Flow](#authentication-flow)
10. [Doctor Onboarding Flow](#doctor-onboarding-flow)
11. [Consultation Flow](#consultation-flow)
12. [Payment Flow](#payment-flow)
13. [Environment Variables](#environment-variables)
14. [Getting Started](#getting-started)
15. [Deployment](#deployment)
16. [API Endpoints](#api-endpoints)
17. [Security](#security)

---

## Overview

Health Mate is a telemedicine platform that connects patients with healthcare providers through secure, HIPAA-compliant video consultations, appointment booking, medical records management, lab test tracking, pharmacy services, and home care requests.

### Key Features

- Firebase Authentication + Django JWT dual-token strategy
- OTP-based email verification with brute force protection
- Role-based access control (Patient, Provider, Admin)
- Video consultations via Daily.co
- Doctor onboarding with admin approval workflow
- Async email delivery via Celery + Resend
- Medical records with prescriptions and care plans
- Lab test booking and result tracking
- Appointment booking with doctor availability slots
- Pharmacy with Paystack payment integration
- Home care service requests
- Media storage via Cloudinary
- Production database via Supabase (PostgreSQL)
- Cache and task queue via Upstash (Redis)

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Django | 4.2.28 | Web framework |
| Django REST Framework | 3.16.1 | REST API |
| djangorestframework-simplejwt | 5.3.1 | JWT authentication |
| firebase-admin | 6.5.0 | Firebase token verification |
| Celery | 5.3.6 | Async task queue |
| Redis (Upstash) | 7 | Message broker + cache |
| PostgreSQL (Supabase) | 15 | Primary database |
| django-celery-beat | 2.8.1 | Scheduled tasks |
| drf-spectacular | 0.28.0 | Swagger/OpenAPI docs |
| Resend | — | Email delivery |
| Cloudinary | 1.44.1 | Media storage |
| Docker | — | Containerisation |
| Daily.co | Latest | Video consultations |
| Gunicorn | 23.0.0 | Production WSGI server |
| Paystack | — | Payment processing |
| Whitenoise | 6.6.0 | Static files |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│    Web (Next.js/Vercel)          Mobile (React Native)              │
│    healthmate-eight.vercel.app                                      │
└────────────────────────┬────────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                              │
│                                                                     │
│              Render (health-mate-api.onrender.com)                  │
│              Gunicorn WSGI Server                                   │
│              Whitenoise (Static Files)                              │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                                │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────────────┐ │
│  │ accounts │ │appoint-  │ │consultation│ │     medicals         │ │
│  │          │ │ments     │ │            │ │                      │ │
│  │ Auth     │ │ Booking  │ │ Video Call │ │ Records + Labs       │ │
│  │ Profile  │ │ Schedule │ │ Onboarding │ │ Prescriptions        │ │
│  └──────────┘ └──────────┘ └────────────┘ └──────────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐                          │
│  │ pharmacy │ │homecare  │ │  helper    │                          │
│  │          │ │          │ │            │                          │
│  │ Products │ │ Services │ │ Tasks      │                          │
│  │ Orders   │ │ Requests │ │ Email      │                          │
│  └──────────┘ └──────────┘ └────────────┘                          │
└────────────────────────┬────────────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  Supabase   │  │   Upstash    │  │  Cloudinary  │
│ PostgreSQL  │  │    Redis     │  │    Media     │
│ (Database)  │  │ (Cache+Queue)│  │  (Files)     │
└─────────────┘  └──────────────┘  └──────────────┘
          │              │
          ▼              ▼
┌─────────────┐  ┌──────────────┐
│  Firebase   │  │   Celery     │
│    Auth     │  │   Worker     │
│ (Tokens)    │  │ (Async Tasks)│
└─────────────┘  └──────────────┘
```

---

## System Design

### Design Principles

1. **Separation of Concerns** — Each app handles one domain
2. **Service Layer Pattern** — Business logic in `services.py`, views stay thin
3. **Permission Classes** — Role-based access at view level
4. **Async Tasks** — Emails and heavy tasks via Celery
5. **Environment-based Config** — No hardcoded secrets

### Request Lifecycle

```
Client Request
     ↓
CORS Middleware → Security Middleware → Auth Middleware
     ↓
URL Router → View
     ↓
Permission Check (IsAuthenticated, IsPatient, IsDoctor, etc.)
     ↓
Serializer Validation
     ↓
Service Layer (Business Logic)
     ↓
Model / ORM → Supabase PostgreSQL
     ↓
Response → CustomResponse wrapper
     ↓
Client
```

### Async Email Flow

```
View triggers email
     ↓
send_a_mail.delay() → Upstash Redis Queue
     ↓
Celery Worker picks up task
     ↓
Resend API → User's inbox
```

### Video Consultation Flow

```
Patient books consultation
     ↓
POST /consultations/{id}/join/
     ↓
Backend calls Daily.co API → Creates room + patient token
     ↓
Doctor calls POST /consultations/{id}/start/
     ↓
Backend calls Daily.co API → Creates doctor token (is_owner=True)
     ↓
Both parties join room
     ↓
POST /consultations/{id}/end/
     ↓
Backend deletes Daily.co room
     ↓
Doctor adds notes via POST /consultations/{id}/notes/
     ↓
Medical record created automatically
```

---

## Database Design

### Core Tables

#### `accounts_companyuser`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| email | VARCHAR(254) UNIQUE | User email |
| firebase_uid | VARCHAR(128) UNIQUE | Firebase UID |
| full_name | VARCHAR(255) | Full name |
| phone_number | VARCHAR(20) | Phone |
| date_of_birth | DATE | DOB |
| gender | VARCHAR(20) | Gender |
| city | VARCHAR(100) | City |
| role | VARCHAR(20) | patient / provider / admin |
| is_email_verified | BOOLEAN | Email verified |
| is_active | BOOLEAN | Account active |
| created_at | TIMESTAMP | Created |

#### `accounts_otpcode`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| user_id | FK → companyuser | User |
| code | VARCHAR(6) | 6-digit OTP |
| purpose | VARCHAR(20) | signup / password_reset |
| is_used | BOOLEAN | Already used |
| expires_at | TIMESTAMP | Expiry time |
| created_at | TIMESTAMP | Created |

#### `doctor_profiles`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| user_id | FK → companyuser | Doctor user |
| specialty | VARCHAR(100) | Medical specialty |
| bio | TEXT | Biography |
| clinical_expertise | TEXT | Expertise areas |
| languages | VARCHAR(200) | Languages spoken |
| education | TEXT | Education history |
| experience_years | INT | Years of experience |
| consultation_type | VARCHAR(10) | video/audio/chat |
| rating | DECIMAL(3,2) | Average rating |
| total_reviews | INT | Review count |
| is_available | BOOLEAN | Available for booking |
| location | VARCHAR(200) | City/location |
| medical_school | VARCHAR(200) | Medical school |
| graduation_year | INT | Year graduated |
| board_certifications | TEXT | Certifications |

#### `doctor_onboarding`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| doctor_id | FK → doctor_profiles | Doctor |
| status | VARCHAR(20) | incomplete/pending/approved/rejected |
| step_personal_done | BOOLEAN | Step 1 complete |
| step_professional_done | BOOLEAN | Step 2 complete |
| step_medical_done | BOOLEAN | Step 3 complete |
| step_availability_done | BOOLEAN | Step 4 complete |
| step_documents_done | BOOLEAN | Step 5 complete |
| rejection_reason | TEXT | Why rejected |
| reviewed_by_id | FK → companyuser | Admin reviewer |
| submitted_at | TIMESTAMP | Submitted time |
| reviewed_at | TIMESTAMP | Review time |

#### `doctor_availability`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| doctor_id | FK → doctor_profiles | Doctor |
| day_of_week | VARCHAR(10) | monday-sunday |
| start_time | TIME | Start time |
| end_time | TIME | End time |
| is_active | BOOLEAN | Active slot |

#### `doctor_documents`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| doctor_id | FK → doctor_profiles | Doctor |
| medical_license | CloudinaryField | License document |
| medical_license_number | VARCHAR(100) | License number |
| medical_license_expiry | DATE | Expiry date |
| medical_certificate | CloudinaryField | Certificate |
| uploaded_at | TIMESTAMP | Upload time |

#### `appointments_appointment`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| patient_id | FK → companyuser | Patient |
| doctor_id | FK → doctor_profiles | Doctor |
| appointment_date | DATE | Date |
| appointment_time | TIME | Time |
| consultation_mode | VARCHAR(20) | video/audio/in_person |
| status | VARCHAR(20) | pending/confirmed/cancelled/completed |
| reason | TEXT | Reason for visit |
| cancellation_reason | TEXT | Why cancelled |
| rescheduled_from_id | FK → appointment | Original appointment |
| created_at | TIMESTAMP | Created |

#### `consultations`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| patient_id | FK → companyuser | Patient |
| doctor_id | FK → doctor_profiles | Doctor |
| consultation_type | VARCHAR(10) | video/audio/chat |
| status | VARCHAR(20) | scheduled/active/completed/cancelled |
| room_name | VARCHAR(200) | Daily.co room |
| room_url | URLField | Daily.co URL |
| patient_token | TEXT | Patient Daily.co token |
| doctor_token | TEXT | Doctor Daily.co token |
| scheduled_at | TIMESTAMP | Scheduled time |
| started_at | TIMESTAMP | Start time |
| ended_at | TIMESTAMP | End time |
| duration_minutes | INT | Call duration |
| reason | TEXT | Reason for consultation |
| is_paid | BOOLEAN | Payment status |

#### `consultation_notes`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| consultation_id | FK → consultations | Consultation |
| doctor_notes | TEXT | Doctor notes |
| diagnosis | TEXT | Diagnosis |
| prescription | TEXT | Prescription |
| follow_up_required | BOOLEAN | Follow-up needed |
| follow_up_date | DATE | Follow-up date |
| is_reviewed | BOOLEAN | Reviewed status |

#### `medicals_medicalrecord`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| patient_id | FK → companyuser | Patient |
| doctor_id | FK → doctor_profiles | Doctor |
| record_type | VARCHAR(30) | consultation/lab/prescription |
| title | VARCHAR(255) | Record title |
| status | VARCHAR(20) | pending/available |
| date | DATE | Record date |
| chief_complaint | TEXT | Chief complaint |
| diagnosis | TEXT | Diagnosis |
| detailed_notes | TEXT | Full notes |

#### `pharmacy_product`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| name | VARCHAR(200) | Product name |
| category | VARCHAR(20) | medicine/supplement/device |
| description | TEXT | Description |
| price | DECIMAL(10,2) | Price in NGN |
| image | CloudinaryField | Product image |
| in_stock | BOOLEAN | Stock status |
| is_featured | BOOLEAN | Featured product |

#### `pharmacy_order`
| Column | Type | Description |
|---|---|---|
| id | BigInt PK | Primary key |
| patient_id | FK → companyuser | Patient |
| order_number | VARCHAR(20) UNIQUE | Order reference |
| status | VARCHAR(20) | pending/processing/delivered |
| payment_status | VARCHAR(20) | pending/paid/failed |
| delivery_method | VARCHAR(20) | standard/express/pickup |
| delivery_address | TEXT | Delivery address |
| subtotal | DECIMAL(10,2) | Subtotal |
| delivery_fee | DECIMAL(10,2) | Delivery fee |
| total_amount | DECIMAL(10,2) | Total |
| paystack_ref | VARCHAR(100) | Paystack reference |

---

## Entity Relationship Diagram (ERD)

```
CompanyUser
│
├── 1:1 ──► DoctorProfile
│               │
│               ├── 1:1 ──► DoctorOnboarding
│               ├── 1:1 ──► DoctorDocument
│               ├── 1:M ──► DoctorAvailability
│               ├── 1:M ──► Consultation (as doctor)
│               └── 1:M ──► Appointment (as doctor)
│
├── 1:M ──► Consultation (as patient)
│               │
│               └── 1:1 ──► ConsultationNote
│
├── 1:M ──► Appointment (as patient)
│
├── 1:M ──► MedicalRecord
│               │
│               ├── 1:M ──► Prescription
│               ├── 1:M ──► LabTest
│               └── 1:1 ──► CarePlan
│
├── 1:M ──► PharmacyOrder
│               │
│               └── 1:M ──► OrderItem ──► Product
│
├── 1:M ──► HomeCareRequest ──► HomeCareService
│
├── 1:1 ──► MedicalInformation
├── 1:1 ──► EmergencyContact
└── 1:M ──► OTPCode
```

### Relationship Details

```
CompanyUser (1) ──────── (1) DoctorProfile
DoctorProfile (1) ─────── (1) DoctorOnboarding
DoctorProfile (1) ─────── (1) DoctorDocument
DoctorProfile (1) ─────── (M) DoctorAvailability
CompanyUser (1) ─────────(M) Consultation [patient]
DoctorProfile (1) ────── (M) Consultation [doctor]
Consultation (1) ──────── (1) ConsultationNote
CompanyUser (1) ──────── (M) Appointment [patient]
DoctorProfile (1) ────── (M) Appointment [doctor]
CompanyUser (1) ──────── (M) MedicalRecord
MedicalRecord (1) ─────── (M) Prescription
MedicalRecord (1) ─────── (M) LabTest
CompanyUser (1) ──────── (M) PharmacyOrder
PharmacyOrder (1) ─────── (M) OrderItem
Product (1) ──────────── (M) OrderItem
CompanyUser (1) ──────── (M) HomeCareRequest
HomeCareService (1) ───── (M) HomeCareRequest
```

---

## Project Structure

```
Health-mate-api/
├── core/                         # Django config
│   ├── settings.py               # All settings (env-based)
│   ├── celery.py                 # Celery config
│   ├── urls.py                   # Root URL config
│   └── wsgi.py                   # WSGI entry point
│
├── accounts/                     # Authentication & User Management
│   ├── models.py                 # CompanyUser, OTPCode, MedicalInfo, etc.
│   ├── views.py                  # Auth views
│   ├── serializers.py            # Auth serializers
│   ├── firebase.py               # Firebase Admin SDK
│   └── urls.py                   # /auth/ routes
│
├── appointments/                 # Appointment Booking
│   ├── models.py                 # Appointment, AppointmentStatus
│   ├── views.py                  # Booking, scheduling views
│   ├── serializers.py
│   └── urls.py                   # /appointments/ routes
│
├── consultation/                 # Video Consultations + Doctor Onboarding
│   ├── models.py                 # DoctorProfile, Consultation, Onboarding, etc.
│   ├── views.py                  # Consultation + Onboarding views
│   ├── serializers.py
│   ├── services.py               # ConsultationService, DailyCoService, OnboardingService
│   ├── permissions.py            # IsDoctor, IsPatient, IsApprovedDoctor, etc.
│   └── urls.py                   # /consultations/ routes
│
├── medicals/                     # Medical Records & Lab Tests
│   ├── models.py                 # MedicalRecord, LabTest, Prescription, etc.
│   ├── views.py
│   ├── serializers.py
│   ├── services.py
│   ├── permissions.py
│   └── urls.py                   # /medicals/ routes
│
├── pharmacy/                     # Pharmacy & Orders
│   ├── models.py                 # Product, Cart, Order, etc.
│   ├── views.py
│   ├── serializers.py
│   ├── services.py               # OrderService, PaystackService
│   ├── permissions.py
│   └── urls.py                   # /api/pharmacy/ routes
│
├── homecare/                     # Home Care Services
│   ├── models.py                 # HomeCareService, HomeCareRequest
│   ├── views.py
│   ├── serializers.py
│   └── urls.py                   # /api/homecare/ routes
│
├── helper/                       # Shared Utilities
│   ├── tasks.py                  # send_a_mail + periodic Celery tasks
│   └── response.py               # CustomResponse helper
│
├── Scripts/
│   ├── start.sh                  # Production startup (Gunicorn)
│   └── dev_start.sh              # Local development startup
│
├── Dockerfile                    # Docker image definition
├── docker-compose.yml            # Local development stack
├── requirements.txt              # Python dependencies
└── manage.py                     # Django management
```

---

## API Modules

### Authentication (`/auth/`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/auth/register/` | POST | No | Register new user |
| `/auth/login/` | POST | No | Login with Firebase token |
| `/auth/verify-otp/` | POST | No | Verify OTP → returns JWT |
| `/auth/resend-otp/` | POST | No | Resend OTP |
| `/auth/reset-password/` | POST | No | 3-step password reset |
| `/auth/logout/` | POST | Yes | Logout + blacklist token |
| `/auth/profile/` | GET | Yes | Get user profile |
| `/auth/profile/personal/` | PATCH | Yes | Update personal info |
| `/auth/profile/medical/` | POST | Yes | Save medical information |
| `/auth/profile/emergency/` | POST | Yes | Save emergency contact |
| `/auth/token/refresh/` | POST | No | Refresh JWT token |
| `/auth/token/verify/` | POST | No | Verify JWT token |

### Appointments (`/appointments/`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/appointments/` | GET | Yes | List my appointments |
| `/appointments/{id}/` | GET | Yes | Get appointment detail |
| `/appointments/{id}/cancel/` | POST | Yes | Cancel appointment |
| `/appointments/{id}/reschedule/` | POST | Yes | Reschedule appointment |
| `/appointments/book/` | POST | Yes | Book appointment |
| `/appointments/doctors/` | GET | Yes | List all doctors |
| `/appointments/doctors/{id}/` | GET | Yes | Get doctor profile |
| `/appointments/doctors/{id}/availability/` | GET | Yes | Get doctor slots |

### Consultation (`/consultations/`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/consultations/` | GET/POST | Yes | List/book consultations |
| `/consultations/{id}/` | GET | Yes | Get consultation |
| `/consultations/{id}/join/` | POST | Yes | Join — get Daily.co token |
| `/consultations/{id}/start/` | POST | Yes | Start consultation |
| `/consultations/{id}/end/` | POST | Yes | End consultation |
| `/consultations/{id}/cancel/` | POST | Yes | Cancel consultation |
| `/consultations/{id}/notes/` | POST | Doctor | Add doctor notes |
| `/consultations/onboarding/personal/` | POST | Provider | Step 1 |
| `/consultations/onboarding/professional/` | POST | Provider | Step 2 |
| `/consultations/onboarding/medical-info/` | POST | Provider | Step 3 |
| `/consultations/onboarding/availability/` | POST | Provider | Step 4 |
| `/consultations/onboarding/documents/` | POST | Provider | Step 5 → Pending |
| `/consultations/onboarding/status/` | GET | Provider | Check status |
| `/consultations/onboarding/resubmit/` | POST | Provider | Resubmit after rejection |

### Medical Records (`/medicals/`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/medicals/records/` | GET/POST | Yes | List/create records |
| `/medicals/records/{id}/` | GET | Yes | Get record detail |
| `/medicals/records/{id}/prescriptions/{pid}/send-to-pharmacy/` | POST | Yes | Send to pharmacy |
| `/medicals/lab-tests/` | GET/POST | Yes | List/book lab tests |
| `/medicals/lab-tests/{id}/` | GET/PATCH | Yes | Get/update lab test |

### Pharmacy (`/api/pharmacy/`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/pharmacy/products/` | GET | Yes | Browse products |
| `/api/pharmacy/cart/` | GET | Yes | View cart |
| `/api/pharmacy/cart/add/` | POST | Yes | Add to cart |
| `/api/pharmacy/cart/remove/{id}/` | DELETE | Yes | Remove from cart |
| `/api/pharmacy/orders/` | GET | Yes | My orders |
| `/api/pharmacy/orders/checkout/` | POST | Yes | Checkout → create order |
| `/api/pharmacy/orders/{id}/pay/` | POST | Yes | Initiate Paystack payment |
| `/api/pharmacy/orders/{id}/track/` | GET | Yes | Track order |
| `/api/pharmacy/webhook/paystack/` | POST | No | Paystack webhook |

### Home Care (`/api/homecare/`)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/homecare/services/` | GET | Yes | List services |
| `/api/homecare/requests/` | GET | Yes | My requests |
| `/api/homecare/requests/create/` | POST | Yes | Create request |

---

## Authentication Flow

```
CLIENT                        BACKEND                      FIREBASE
  │                              │                             │
  │── Sign in/up with Firebase ──────────────────────────────►│
  │                              │                   Returns ID Token
  │                              │                             │
  │── POST /auth/register/ ─────►│                             │
  │   { firebase_token, ... }    │── verify_id_token() ───────►│
  │                              │◄─ decoded claims ───────────│
  │                              │── Create User               │
  │                              │── Generate OTP              │
  │                              │── Send OTP Email (Celery)   │
  │◄─ 201 { email } ────────────│                             │
  │                              │                             │
  │── POST /auth/verify-otp/ ───►│                             │
  │   { email, otp_code }        │── Validate OTP              │
  │◄─ 200 { tokens, user } ─────│ ← JWT returned here ✅      │
  │                              │                             │
  │── POST /auth/login/ ────────►│                             │
  │   { firebase_token }         │── verify_id_token() ───────►│
  │◄─ 200 { access, refresh } ──│                             │
```

### Token Lifecycle

| Token | Expires | Handled By |
|---|---|---|
| Firebase ID Token | 1 hour | Firebase SDK (auto-refresh) |
| JWT Access Token | 15 minutes | POST /auth/token/refresh/ |
| JWT Refresh Token | 7 days | Force re-login |

---

## Doctor Onboarding Flow

```
Doctor registers with role=provider
            ↓
Step 1: POST /consultations/onboarding/personal/
        Personal Information
            ↓
Step 2: POST /consultations/onboarding/professional/
        Professional Details (specialty, bio, education)
            ↓
Step 3: POST /consultations/onboarding/medical-info/
        Chief Medical Information
            ↓
Step 4: POST /consultations/onboarding/availability/
        Set Weekly Availability Schedule
            ↓
Step 5: POST /consultations/onboarding/documents/
        Upload Medical License + Certificate
            ↓
        Status → PENDING (auto)
        Email sent to doctor
            ↓
Admin reviews via Django Admin (/admin/)
        ↓              ↓
   APPROVED ✅    REJECTED ❌
   Email sent     Email sent with reason
   Dashboard      Doctor can resubmit
   unlocked       via /onboarding/resubmit/
```

---

## Consultation Flow

```
1. Patient books → POST /consultations/
2. Patient joins → POST /consultations/{id}/join/
   Backend creates Daily.co room
   Returns room_url + patient_token
3. Doctor joins  → POST /consultations/{id}/start/
   Returns room_url + doctor_token (is_owner=True)
4. Call active   → status = "active"
5. Call ends     → POST /consultations/{id}/end/
   Daily.co room deleted
   Duration calculated
6. Doctor notes  → POST /consultations/{id}/notes/
   Medical record created automatically
```

---

## Payment Flow

```
Patient adds products to cart
            ↓
POST /api/pharmacy/orders/checkout/
Creates order with status=pending
            ↓
POST /api/pharmacy/orders/{id}/pay/
Calls Paystack API → returns authorization_url
            ↓
Patient completes payment on Paystack
            ↓
POST /api/pharmacy/webhook/paystack/
Paystack notifies backend
            ↓
    ┌───────────────┐
    ↓               ↓
Payment OK ✅   Payment Failed ❌
Order=processing  Order=failed
Email sent        Retry available
```

---

## Environment Variables

### Required on Render (Production)

```bash
# Core
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=health-mate-api.onrender.com

# Database (Supabase)
DATABASE_URL=postgresql://postgres.xxx:PASSWORD@aws-1-eu-west-1.pooler.supabase.com:5432/postgres
DB_SSL_REQUIRE=true

# Redis (Upstash)
REDIS_URL=rediss://default:PASSWORD@ace-oyster-66422.upstash.io:6379?ssl_cert_reqs=none
CELERY_BROKER_URL=rediss://default:PASSWORD@ace-oyster-66422.upstash.io:6379/0?ssl_cert_reqs=CERT_NONE
CELERY_RESULT_BACKEND=rediss://default:PASSWORD@ace-oyster-66422.upstash.io:6379/0?ssl_cert_reqs=CERT_NONE

# Firebase
FIREBASE_CREDENTIALS_BASE64=<base64 encoded firebase-credentials.json>
FIREBASE_API_KEY=
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=health-mate-api

# Email (Resend)
DEFAULT_FROM_EMAIL=noreply@ordfellow.com
RESEND_API_KEY=re_xxxx

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Paystack
PAYSTACK_SECRET_KEY=sk_live_xxxx
PAYSTACK_PUBLIC_KEY=pk_live_xxxx

# Daily.co
DAILY_API_KEY=
DAILY_API_URL=https://api.daily.co/v1
DAILY_SUBDOMAIN=

# CORS
CORS_ALLOWED_ORIGINS=https://healthmate-eight.vercel.app
CSRF_TRUSTED_ORIGINS=https://healthmate-eight.vercel.app

# JWT + OTP
JWT_ACCESS_TOKEN_LIFETIME=900
JWT_REFRESH_TOKEN_LIFETIME=604800
OTP_EXPIRY_SECONDS=300

# Render
PORT=10000
```

### Local `.env` (Docker)

```bash
SECRET_KEY=local-dev-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Local PostgreSQL
DB_NAME=health_mate
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DB_SSL_REQUIRE=false

# Local Redis
REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Firebase (local file)
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
```

---

## Getting Started

### Prerequisites

- Docker Desktop
- Firebase Project
- Resend Account
- Supabase Account (production)
- Upstash Account (production)

### Local Development

```bash
# 1. Clone
git clone https://github.com/archsaintnexus/Health-mate-api.git
cd Health-mate-api

# 2. Setup env
cp .env.example .env
# Edit .env with your values

# 3. Add Firebase credentials
# Download from Firebase Console → Service Accounts
# Rename to firebase-credentials.json

# 4. Start all services
docker-compose up --build

# 5. Run migrations (first time)
docker-compose exec web python manage.py migrate

# 6. Create superuser
docker-compose exec web python manage.py createsuperuser

# 7. Visit API
# Swagger: http://localhost:8000/api/docs/
# Admin:   http://localhost:8000/admin/
```

### Docker Services

| Service | Port | Description |
|---|---|---|
| web | 8000 | Django API server |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Redis broker + cache |
| celery | — | Celery worker |
| celery-beat | — | Scheduled task runner |

---

## Deployment

### Production Stack

| Service | Provider | Free Tier |
|---|---|---|
| API | Render | ✅ Free |
| Database | Supabase | ✅ 500MB Free Forever |
| Redis | Upstash | ✅ 10K commands/day |
| Media | Cloudinary | ✅ 25GB Free |
| Email | Resend | ✅ 3,000/month |
| Auth | Firebase | ✅ Free tier |
| Video | Daily.co | ✅ 10,000 min/month |

### Render Settings

```
Repository:    archsaintnexus/Health-mate-api
Branch:        prod
Runtime:       Docker
Dockerfile:    ./Dockerfile
Start Command: ./Scripts/start.sh
```

### Deploy Steps

```bash
# 1. Push to GitHub
git push origin prod

# 2. Render auto-deploys
# Watch logs for:
# ==> Collecting static files... ✅
# ==> Running migrations...      ✅
# ==> Starting Gunicorn...       ✅
# ==> Your service is live 🎉

# 3. Visit
# https://health-mate-api.onrender.com/api/docs/
```

### Generate Firebase Base64 (Windows)

```powershell
[Convert]::ToBase64String(
  [IO.File]::ReadAllBytes(
    "C:\path\to\firebase-credentials.json"
  )
) | Set-Clipboard
```

---

## Security

- Firebase ID tokens verified server-side on every auth request
- JWT access tokens expire in 15 minutes
- JWT refresh tokens expire in 7 days with rotation + blacklisting
- OTP codes expire in 5 minutes with max 5 attempts
- All passwords hashed with Django's PBKDF2
- HTTPS enforced in production (SECURE_SSL_REDIRECT)
- HSTS enabled with 1-year duration
- CORS restricted to approved origins
- Rate limiting on anonymous and authenticated users
- Firebase credentials never committed to version control
- All secrets loaded from environment variables
- Supabase connection uses SSL in production
- Upstash Redis uses TLS (rediss://)

---

## API Documentation

```
Local:      http://localhost:8000/api/docs/
Production: https://health-mate-api.onrender.com/api/docs/
Schema:     https://health-mate-api.onrender.com/api/schema/
```

---

## Testing

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app
docker-compose exec web python manage.py test accounts

# With verbosity
docker-compose exec web python manage.py test --verbosity=2
```

### Test Order (Postman)

```
1.  GET  Firebase token (identitytoolkit)
2.  POST /auth/register/
3.  POST /auth/verify-otp/         ← returns JWT tokens
4.  POST /auth/login/
5.  GET  /auth/profile/
6.  GET  /appointments/doctors/
7.  GET  /appointments/doctors/{id}/availability/
8.  POST /appointments/book/
9.  GET  /appointments/
10. POST /consultations/
11. POST /consultations/{id}/join/
12. POST /consultations/{id}/end/
13. GET  /medicals/records/
14. POST /medicals/lab-tests/
15. GET  /api/pharmacy/products/
16. POST /api/pharmacy/orders/checkout/
```

---

## Health Mate API — © 2026 ArchSaint Nexus
