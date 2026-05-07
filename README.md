# 🏥 Hospital Appointment System

A backend system for managing hospital appointments between patients and doctors, built with **FastAPI**.

---

## 👥 Team Members

| Name | Student ID |
|------|-----------|
| Abdelrahman Mohamed Farouk | 931250585 |
| Fares Nasser Sameh | 931250613 |
| Youssef Mohamed Fathy | 931230377 |
| Philopater Farag Georgiou | 931230213 |
| Ezzelden Adel Hassan | 931230183 |
| Mohamed Nasser Ahmed | 931230271 |

---

## 📋 Project Description

A RESTful API backend system that manages hospital appointments with:
- Secure JWT authentication
- Role-based access control (Admin / User)
- Doctor and patient management
- Appointment booking with conflict prevention
- Redis caching for performance
- Comprehensive logging and monitoring
- Full API test suite

---

## 🚀 Features

- ✅ User registration and login with JWT
- ✅ Role-based authorization (Admin / User)
- ✅ Full CRUD for Doctors, Patients, Appointments
- ✅ Prevent double booking (1 hour gap enforcement)
- ✅ Appointment status management (Scheduled / Completed / Cancelled)
- ✅ Redis caching (Cache-Aside Pattern)
- ✅ Structured logging with Loguru
- ✅ Monitoring dashboard
- ✅ 54 automated tests with pytest
- ✅ Docker + docker-compose support
- ✅ Frontend UI (HTML/CSS/JS)

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Auth:** JWT (python-jose), bcrypt
- **Cache:** Redis
- **Logging:** Loguru
- **Testing:** pytest, httpx
- **Container:** Docker, docker-compose
- **Frontend:** HTML, CSS, JavaScript

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.12+
- Docker Desktop

### 1. Clone the repository
```bash
git clone https://github.com/youbbb890987/hospital-appointment-system.git
cd hospital-appointment-system
```

### 2. Create virtual environment
```bash
py -3.12 -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Redis with Docker
```bash
docker-compose up -d
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

### 6. Open API docs
```
http://127.0.0.1:8000/docs
```

### 7. Open Frontend
Open `frontend/index.html` in your browser.

---

## 🐳 Docker Setup

Run the entire stack with Docker:

```bash
docker-compose up --build -d
```

This starts:
- FastAPI app on port `8000`
- Redis on port `6379`

---

## 🧪 Running Tests

```bash
python -m pytest app/tests/ -v
```

Expected output: **54 passed**

---

## 📁 Project Structure

```
hospital_appointment_system/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── security.py
│   │   └── logger.py
│   ├── models/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── appointment.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── appointment.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   └── monitoring.py
│   ├── cache/
│   │   └── redis_cache.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_doctors.py
│   │   ├── test_patients.py
│   │   └── test_appointments.py
│   └── main.py
├── frontend/
│   └── index.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🔐 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get token |

### Doctors
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/doctors/` | Get all doctors | Public |
| GET | `/doctors/{id}` | Get doctor by ID | Public |
| POST | `/doctors/` | Create doctor | Admin |
| PUT | `/doctors/{id}` | Update doctor | Admin |
| DELETE | `/doctors/{id}` | Delete doctor | Admin |

### Patients
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/patients/` | Get all patients | Admin |
| GET | `/patients/my` | Get my patients | User |
| GET | `/patients/{id}` | Get patient by ID | Admin/Owner |
| POST | `/patients/` | Create patient | Any |
| PUT | `/patients/{id}` | Update patient | Admin/Owner |
| DELETE | `/patients/{id}` | Delete patient | Admin/Owner |

### Appointments
| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| GET | `/appointments/` | Get all appointments | Admin |
| GET | `/appointments/my` | Get my appointments | User |
| GET | `/appointments/{id}` | Get by ID | Admin/Owner |
| POST | `/appointments/` | Book appointment | Any |
| PUT | `/appointments/{id}` | Update appointment | Admin/Owner |
| PATCH | `/appointments/{id}/status` | Update status | Admin |
| DELETE | `/appointments/{id}` | Delete appointment | Admin/Owner |

---

## 👤 Roles & Permissions

| Feature | Admin | User |
|---------|-------|------|
| Manage Doctors | ✅ Full CRUD | ❌ Read only |
| Manage Patients | ✅ All patients | ✅ Own patients only |
| Manage Appointments | ✅ All appointments | ✅ Own appointments only |
| Update Appointment Status | ✅ | ❌ |
| Monitoring Dashboard | ✅ | ❌ |
