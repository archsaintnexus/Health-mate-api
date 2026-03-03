# Health Mate - Backend API Requirements

This document outlines all API endpoints required by the Health Mate frontend application. The backend must implement these endpoints exactly as specified to ensure proper integration with the frontend.

---

## Base Configuration

- **Base URL**: `http://localhost:8000` (configurable via `VITE_API_BASE_URL` environment variable)
- **Content-Type**: `application/json`
- **Authentication**: JWT Bearer Token in Authorization header

---

## Authentication Endpoints

### 1. User Signup

**Endpoint**: `POST /auth/signup`

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "securePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "id": "user_123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input or email already exists
- `500 Internal Server Error`: Database or server error

---

### 2. User Login

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "securePassword123!"
}
```

**Response (200 OK)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

**Notes**: 
- Token should be a valid JWT that the frontend will store in localStorage
- Token should be valid for an extended period (suggested: 30 days)
- Frontend will attach this token to all subsequent requests as: `Authorization: Bearer <token>`

---

## Protected Endpoints

All endpoints below require the `Authorization: Bearer <token>` header.

### 3. Get User Profile

**Endpoint**: `GET /users/me`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK)**:
```json
{
  "id": "user_123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+91 98765 43210",
  "address": "123 Main Street, City, State 12345",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

---

### 4. Update User Profile

**Endpoint**: `PUT /users/me`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+91 98765 43210",
  "address": "123 Main Street, City, State 12345"
}
```

**Response (200 OK)**:
```json
{
  "id": "user_123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+91 98765 43210",
  "address": "123 Main Street, City, State 12345",
  "updated_at": "2024-03-10T14:20:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Invalid token
- `404 Not Found`: User not found
- `500 Internal Server Error`: Server error

---

## Appointments Endpoints

### 5. Get Available Doctors

**Endpoint**: `GET /appointments/doctors`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `specialty`: Filter by specialty (e.g., "Cardiology", "Orthopedics")
- `date`: Filter by available date (YYYY-MM-DD format)

**Response (200 OK)**:
```json
[
  {
    "id": "doctor_1",
    "name": "Dr. Sarah Anderson",
    "specialty": "Cardiology",
    "available_dates": ["2024-03-10", "2024-03-11", "2024-03-12"],
    "available_times": ["09:00", "10:00", "14:00", "15:00"],
    "bio": "Experienced cardiologist with 10+ years of practice",
    "rating": 4.8
  },
  {
    "id": "doctor_2",
    "name": "Dr. James Mitchell",
    "specialty": "Orthopedics",
    "available_dates": ["2024-03-10", "2024-03-13"],
    "available_times": ["10:00", "11:00", "16:00"],
    "bio": "Orthopedic surgeon specializing in joint replacement",
    "rating": 4.7
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

### 6. Book Appointment

**Endpoint**: `POST /appointments`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "doctor_id": "doctor_1",
  "date": "2024-03-15",
  "time": "10:00",
  "reason": "Regular checkup"
}
```

**Response (201 Created)**:
```json
{
  "id": "appointment_123",
  "doctor_id": "doctor_1",
  "doctor_name": "Dr. Sarah Anderson",
  "date": "2024-03-15",
  "time": "10:00",
  "reason": "Regular checkup",
  "status": "confirmed",
  "created_at": "2024-03-10T14:20:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid appointment details or slot not available
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Doctor not found
- `409 Conflict`: Time slot already booked
- `500 Internal Server Error`: Server error

---

### 7. Get User Appointments

**Endpoint**: `GET /appointments`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `status`: Filter by status (upcoming, completed, cancelled)
- `skip`: Pagination offset (default: 0)
- `limit`: Number of results (default: 10)

**Response (200 OK)**:
```json
[
  {
    "id": "appointment_123",
    "doctor_id": "doctor_1",
    "doctor_name": "Dr. Sarah Anderson",
    "specialty": "Cardiology",
    "date": "2024-03-15",
    "time": "10:00",
    "reason": "Regular checkup",
    "status": "confirmed",
    "created_at": "2024-03-10T14:20:00Z"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

### 8. Reschedule Appointment

**Endpoint**: `PUT /appointments/{appointment_id}`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**URL Parameters**:
- `appointment_id`: ID of the appointment to reschedule

**Request Body**:
```json
{
  "date": "2024-03-20",
  "time": "14:00"
}
```

**Response (200 OK)**:
```json
{
  "id": "appointment_123",
  "doctor_id": "doctor_1",
  "doctor_name": "Dr. Sarah Anderson",
  "date": "2024-03-20",
  "time": "14:00",
  "status": "confirmed",
  "updated_at": "2024-03-10T15:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid date/time
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Appointment not found
- `409 Conflict`: New slot not available
- `500 Internal Server Error`: Server error

---

### 9. Cancel Appointment

**Endpoint**: `DELETE /appointments/{appointment_id}`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**URL Parameters**:
- `appointment_id`: ID of the appointment to cancel

**Response (200 OK)**:
```json
{
  "message": "Appointment cancelled successfully",
  "id": "appointment_123"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Appointment not found
- `409 Conflict`: Cannot cancel completed appointment
- `500 Internal Server Error`: Server error

---

## Medical Records Endpoints

### 10. Get Medical Records

**Endpoint**: `GET /records`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `type`: Filter by type (lab_result, consultation, imaging, prescription)
- `skip`: Pagination offset (default: 0)
- `limit`: Number of results (default: 10)

**Response (200 OK)**:
```json
[
  {
    "id": "record_1",
    "title": "Blood Work Report",
    "type": "lab_result",
    "date": "2024-03-05",
    "description": "Complete blood count results",
    "file_url": "https://storage.example.com/records/record_1.pdf",
    "created_at": "2024-03-05T10:00:00Z"
  },
  {
    "id": "record_2",
    "title": "General Checkup Notes",
    "type": "consultation",
    "date": "2024-02-28",
    "description": "Notes from general checkup",
    "file_url": "https://storage.example.com/records/record_2.pdf",
    "created_at": "2024-02-28T14:30:00Z"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

### 11. Download Medical Record

**Endpoint**: `GET /records/{record_id}/download`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**URL Parameters**:
- `record_id`: ID of the record to download

**Response**: File download (binary)

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Record not found
- `500 Internal Server Error`: Server error

---

## Lab Tests Endpoints

### 12. Get Available Lab Tests

**Endpoint**: `GET /lab-tests`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK)**:
```json
[
  {
    "id": "test_1",
    "name": "Complete Blood Count",
    "description": "Comprehensive blood analysis",
    "price": 500,
    "result_time": "24 hours",
    "requirements": "Fasting recommended"
  },
  {
    "id": "test_2",
    "name": "Lipid Profile",
    "description": "Cholesterol and triglyceride levels",
    "price": 800,
    "result_time": "24 hours",
    "requirements": "Fasting required"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

### 13. Book Lab Test

**Endpoint**: `POST /lab-tests/bookings`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "test_id": "test_1",
  "preferred_date": "2024-03-20",
  "collection_point": "Home"
}
```

**Response (201 Created)**:
```json
{
  "id": "booking_123",
  "test_id": "test_1",
  "test_name": "Complete Blood Count",
  "price": 500,
  "preferred_date": "2024-03-20",
  "collection_point": "Home",
  "status": "confirmed",
  "booking_reference": "HM-LAB-2024-001",
  "created_at": "2024-03-10T14:20:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid test or date
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Test not found
- `500 Internal Server Error`: Server error

---

### 14. Get Lab Test Results

**Endpoint**: `GET /lab-tests/results`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `status`: Filter by status (pending, completed)

**Response (200 OK)**:
```json
[
  {
    "id": "result_123",
    "test_name": "Complete Blood Count",
    "booking_date": "2024-03-05",
    "result_date": "2024-03-06",
    "status": "completed",
    "result_url": "https://storage.example.com/results/result_123.pdf"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

## Pharmacy Endpoints

### 15. Get Medications Catalog

**Endpoint**: `GET /pharmacy/medications`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `search`: Search by medication name
- `category`: Filter by category (pain_relief, vitamins, antibiotics, etc.)
- `skip`: Pagination offset (default: 0)
- `limit`: Number of results (default: 20)

**Response (200 OK)**:
```json
[
  {
    "id": "med_1",
    "name": "Aspirin 500mg",
    "dosage": "500mg",
    "quantity": "100 tablets",
    "price": 120,
    "manufacturer": "Generic Pharma",
    "rating": 4.8,
    "requires_prescription": false
  },
  {
    "id": "med_2",
    "name": "Ibuprofen 400mg",
    "dosage": "400mg",
    "quantity": "50 tablets",
    "price": 85,
    "manufacturer": "Pain Relief Co",
    "rating": 4.7,
    "requires_prescription": false
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

### 16. Create Medication Order

**Endpoint**: `POST /pharmacy/orders`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "items": [
    {
      "medication_id": "med_1",
      "quantity": 2
    },
    {
      "medication_id": "med_2",
      "quantity": 1
    }
  ],
  "delivery_address": "123 Main Street, City, State 12345",
  "delivery_date": "2024-03-15"
}
```

**Response (201 Created)**:
```json
{
  "id": "order_123",
  "items": [
    {
      "medication_id": "med_1",
      "name": "Aspirin 500mg",
      "quantity": 2,
      "price": 120,
      "subtotal": 240
    }
  ],
  "total": 325,
  "delivery_address": "123 Main Street, City, State 12345",
  "estimated_delivery": "2024-03-15",
  "status": "confirmed",
  "order_reference": "HM-PHARM-2024-001",
  "created_at": "2024-03-10T14:20:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid items or quantities
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Medication not found
- `500 Internal Server Error`: Server error

---

### 17. Get Medication Orders

**Endpoint**: `GET /pharmacy/orders`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `status`: Filter by status (pending, shipped, delivered)

**Response (200 OK)**:
```json
[
  {
    "id": "order_123",
    "total": 325,
    "status": "shipped",
    "order_reference": "HM-PHARM-2024-001",
    "estimated_delivery": "2024-03-15",
    "created_at": "2024-03-10T14:20:00Z"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

## Telehealth Endpoints

### 18. Get Available Telehealth Providers

**Endpoint**: `GET /telehealth/providers`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `specialty`: Filter by specialty
- `available_today`: Boolean to show only providers available today

**Response (200 OK)**:
```json
[
  {
    "id": "provider_1",
    "name": "Dr. Sarah Anderson",
    "specialty": "Cardiology",
    "available_slots": ["10:00", "14:00", "16:00"],
    "consultation_fee": 500,
    "rating": 4.8
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

### 19. Book Telehealth Consultation

**Endpoint**: `POST /telehealth/consultations`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "provider_id": "provider_1",
  "date": "2024-03-15",
  "time": "10:00",
  "reason": "Health consultation"
}
```

**Response (201 Created)**:
```json
{
  "id": "consultation_123",
  "provider_id": "provider_1",
  "provider_name": "Dr. Sarah Anderson",
  "date": "2024-03-15",
  "time": "10:00",
  "reason": "Health consultation",
  "video_call_link": "https://healthmate.video/room/consultation_123",
  "status": "scheduled",
  "consultation_fee": 500,
  "created_at": "2024-03-10T14:20:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid details
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Provider not found
- `409 Conflict`: Slot not available
- `500 Internal Server Error`: Server error

---

### 20. Get Telehealth Consultations

**Endpoint**: `GET /telehealth/consultations`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `status`: Filter by status (upcoming, completed, cancelled)

**Response (200 OK)**:
```json
[
  {
    "id": "consultation_123",
    "provider_name": "Dr. Sarah Anderson",
    "date": "2024-03-15",
    "time": "10:00",
    "status": "scheduled",
    "video_call_link": "https://healthmate.video/room/consultation_123"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

## Home Care Endpoints

### 21. Get Home Care Services

**Endpoint**: `GET /home-care/services`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK)**:
```json
[
  {
    "id": "service_1",
    "title": "Nursing Care",
    "description": "Professional nurses for wound care and monitoring",
    "price_per_visit": 2000,
    "duration": "1-2 hours"
  },
  {
    "id": "service_2",
    "title": "Physical Therapy",
    "description": "Rehabilitation and physiotherapy at your home",
    "price_per_session": 1500,
    "duration": "1 hour"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

### 22. Book Home Care Service

**Endpoint**: `POST /home-care/bookings`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "service_id": "service_1",
  "preferred_date": "2024-03-20",
  "preferred_time": "10:00",
  "special_requirements": "Patient has limited mobility"
}
```

**Response (201 Created)**:
```json
{
  "id": "booking_123",
  "service_id": "service_1",
  "service_name": "Nursing Care",
  "preferred_date": "2024-03-20",
  "preferred_time": "10:00",
  "price": 2000,
  "status": "pending_confirmation",
  "booking_reference": "HM-HC-2024-001",
  "created_at": "2024-03-10T14:20:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid service or date
- `401 Unauthorized`: Invalid token
- `404 Not Found`: Service not found
- `500 Internal Server Error`: Server error

---

### 23. Get Home Care Bookings

**Endpoint**: `GET /home-care/bookings`

**Headers Required**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters** (optional):
- `status`: Filter by status (pending_confirmation, confirmed, completed, cancelled)

**Response (200 OK)**:
```json
[
  {
    "id": "booking_123",
    "service_name": "Nursing Care",
    "preferred_date": "2024-03-20",
    "status": "confirmed",
    "caregiver_name": "Sarah Smith",
    "caregiver_contact": "+91 98765 43210"
  }
]
```

**Error Responses**:
- `401 Unauthorized`: Invalid token
- `500 Internal Server Error`: Server error

---

## Error Handling

All endpoints should return appropriate HTTP status codes and error messages in the following format:

```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {}
}
```

**Common Status Codes**:
- `200 OK`: Successful GET or PUT request
- `201 Created`: Successful POST request (resource created)
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User doesn't have permission
- `404 Not Found`: Resource not found
- `409 Conflict`: Conflict with existing data (e.g., email already exists, slot not available)
- `500 Internal Server Error`: Server error

---

## Authentication Flow

1. User signs up → receives user ID (no token)
2. User logs in → receives JWT token
3. Frontend stores token in localStorage as "healthmate_token"
4. For all protected endpoints, frontend sends token in Authorization header
5. If token is invalid or expired (401 response), frontend clears token and redirects to login

---

## Implementation Notes for Backend Developer

1. **JWT Implementation**: 
   - Use HS256 algorithm
   - Include user ID and email in token payload
   - Set expiration to 30 days
   - Use a strong secret key

2. **Database Considerations**:
   - Implement proper password hashing (bcrypt recommended)
   - Add indexes on frequently queried fields
   - Consider implementing soft deletes for records

3. **Security**:
   - Validate all input data
   - Implement rate limiting on auth endpoints
   - Use HTTPS in production
   - Implement CORS properly to allow frontend domain

4. **Data Validation**:
   - Email should be validated and lowercased
   - Phone numbers should be validated for format
   - Dates should be in ISO 8601 format (YYYY-MM-DD)
   - Times should be in 24-hour format (HH:MM)

5. **Testing**:
   - Test all endpoints with invalid tokens
   - Test pagination with skip/limit parameters
   - Test error cases (missing fields, invalid IDs, etc.)
   - Load test appointment booking during peak hours

---

## Frontend Integration Ready

The frontend is built to:
- Attach JWT tokens to all requests automatically
- Handle 401 responses by redirecting to login
- Display user-friendly error messages from backend
- Retry failed requests based on error codes
- Parse and display all response formats as documented

All API endpoints should follow these specifications exactly for seamless integration.
