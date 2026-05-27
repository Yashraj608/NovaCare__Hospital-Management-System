<div align="center">

# 🏥 NovaCare — Hospital Management System

A full-stack web application built with **Django** that digitizes end-to-end hospital operations — from patient registration and appointment booking to doctor consultations, pharmacy billing, and unified invoice generation.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-6.0.3-green?style=flat-square&logo=django)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
- [User Roles](#user-roles)
- [URL Routes](#url-routes)
- [Installation & Setup](#installation--setup)
- [How to Use](#how-to-use)
- [Author](#author)

---

## Overview

NovaCare is a multi-role hospital management platform built using the **Django MVT (Model-View-Template)** architecture. It manages the complete lifecycle of a patient's hospital visit — from registering an account and booking an appointment, to receiving a diagnosis, getting medicines prescribed, and paying a unified bill that covers both consultation and pharmacy costs.

The project spans **4 Django apps**, **12+ database models**, **40+ URL endpoints**, and a fully server-rendered frontend using Django's Template Engine.

---

## Features

### 👤 Authentication & Roles
- Custom `AbstractUser` model with 4 role flags: `is_patient`, `is_doctor`, `is_pharmacist`, `is_receptionist`
- Session-based login/logout with Django's built-in `authenticate()` and `login()`
- CSRF protection enabled on all forms via Django middleware
- Role-based dashboard redirection on login
- `@login_required` protection on all sensitive views

### 🗓️ Appointment Management
- Patients book appointments by selecting doctor, date, and time slot
- `unique_together` constraint prevents double-booking the same slot
- Doctors approve, cancel, or complete appointments from their dashboard
- Doctors add consultation notes: diagnosis, prescription, test reports
- Prescribed medicines linked directly to the appointment record

### 💊 Pharmacy Module
- Full medicine inventory: add, edit, delete, update stock
- Public pharmacy listing page for patients to browse medicines
- Patient shopping cart (one cart per patient via `OneToOneField`)
- **POS Billing** — pharmacist-side billing with manual quantity entry and automatic stock deduction
- **Patient Checkout** — cart-based checkout that generates a unified bill covering medicines + consultation fee

### 🧾 Unified Billing
- Auto-generated `UnifiedBill` when a doctor marks a consultation as Completed
- Bill consolidates consultation fee + prescribed medicine cost into one `grand_total`
- Patients can view full bill breakdown and pay online
- Expenditure history page for patients to track all past bills

### 📊 Admin Dashboard
- Revenue chart (monthly SUM aggregates over 12 months)
- Appointments per department (pie chart data)
- Low stock medicine alerts
- Today's appointment agenda
- Full doctor management: add, edit, delete, view all doctors

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 6.0.3 |
| Language | Python 3.x |
| Database | SQLite3 |
| ORM | Django ORM |
| Frontend | Django Template Engine (HTML/CSS/JS) |
| Authentication | Django Auth Framework (session-based) |
| Static Files | Django StaticFiles |
| Media Files | Django Media Server |
| Admin Panel | Django Admin (`/admin/`) |

---

## Project Structure

```
DB project/
│
├── hospital_project/          # Project config
│   ├── settings.py
│   ├── urls.py                # Root URL router
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                  # User auth, roles, dashboards
│   ├── models.py              # User, Doctor, Patient, Pharmacist, Department
│   ├── views.py               # Login, Register, Dashboards, Admin panel
│   └── urls.py
│
├── appointments/              # Booking & consultation
│   ├── models.py              # Appointment, PrescribedMedicine
│   ├── views.py               # Book, Approve, Cancel, Add Notes
│   └── urls.py
│
├── pharmacy/                  # Inventory, cart, billing
│   ├── models.py              # Medicine, PharmacyBill, PatientCart, UnifiedBill
│   ├── views.py               # POS, Cart, Checkout, Expenditure
│   └── urls.py
│
├── core/                      # Public pages & doctor management
│   ├── models.py              # Service
│   ├── views.py               # Home, About, Doctors, Services
│   └── urls.py
│
├── templates/                 # All HTML templates (server-rendered)
├── static/                    # CSS, JS, Images
├── media/                     # User-uploaded photos
└── manage.py
```

---

## Database Models

```
accounts_user               ← Custom AbstractUser (4 role flags)
    │
    ├──► accounts_doctor         (OneToOne → User)
    │       └──► accounts_department  (ForeignKey)
    │
    ├──► accounts_patient        (OneToOne → User)
    │       └──► pharmacy_patientcart     (OneToOne → Patient)
    │               └──► pharmacy_patientcartitem  (FK → Cart, FK → Medicine)
    │
    └──► accounts_pharmacist     (OneToOne → User)

appointments_appointment    (FK → Patient, FK → Doctor)
    └──► appointments_prescribedmedicine  (FK → Appointment, FK → Medicine)

pharmacy_medicine
pharmacy_pharmacybill       (FK → Pharmacist)
    └──► pharmacy_pharmacybillitem  (FK → Bill, FK → Medicine)

pharmacy_unifiedbill        (FK → Patient, OneToOne → Appointment)
```

**Auto-generated indexes** on all ForeignKey columns.
**Unique composite index** on `(patient, doctor, date, time)` in Appointment.

---

## User Roles

| Role | Access |
|---|---|
| **Admin** | Full dashboard — revenue charts, doctor management, all appointments, low-stock alerts |
| **Doctor** | Own appointment list, approve/cancel, add consultation notes, prescribe medicines |
| **Patient** | Book appointments, view medical history, pharmacy cart, checkout, bill history |
| **Pharmacist** | Medicine inventory management, POS billing, stock updates |

---

## URL Routes

```
/                           → Home (core)
/about/                     → About page
/services/                  → Services catalogue
/doctors/                   → Doctor listing with search & department filter
/branches/                  → Hospital branches

/accounts/login/            → Login
/accounts/register/         → Register (select role)
/accounts/logout/           → Logout
/accounts/patient-dashboard/
/accounts/doctor-dashboard/
/accounts/admin-dashboard/
/accounts/admin-appointments/
/accounts/admin-doctors/

/appointments/book/
/appointments/approve/<id>/
/appointments/cancel/<id>/
/appointments/add_notes/<id>/
/appointments/<id>/
/appointments/patient_history/<id>/

/pharmacy/                  → Public medicine list
/pharmacy/dashboard/        → Pharmacist dashboard
/pharmacy/medicines/        → Inventory list
/pharmacy/medicines/add/
/pharmacy/medicines/<id>/edit/
/pharmacy/medicines/<id>/delete/
/pharmacy/medicines/<id>/stock/
/pharmacy/billing/          → POS billing
/pharmacy/cart/
/pharmacy/cart/add/<id>/
/pharmacy/cart/remove/<id>/
/pharmacy/checkout/
/pharmacy/bill/<id>/
/pharmacy/bill/<id>/pay/
/pharmacy/history/

/admin/                     → Django Admin panel
```

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/your-username/novacare.git
cd novacare
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install django pillow
```

**4. Apply migrations**
```bash
python manage.py migrate
```

> This automatically seeds 40 hospital departments via a `RunPython` migration.

**5. Create a superuser (Admin access)**
```bash
python manage.py createsuperuser
```

**6. Run the development server**
```bash
python manage.py runserver
```

**7. Open in browser**
```
http://127.0.0.1:8000/
```

---

## How to Use

1. **Register** as a Patient, Doctor, or Pharmacist at `/accounts/register/`
2. **Admin** — log in with superuser credentials → redirected to Admin Dashboard
3. **Doctor** — log in → Doctor Dashboard → manage appointments, add consultation notes
4. **Patient** — log in → Patient Dashboard → book appointments, browse pharmacy, checkout
5. **Pharmacist** — log in → Pharmacist Dashboard → manage inventory, run POS billing
6. **Django Admin** at `/admin/` — full model-level management

---

## Author

**Yash Raj**

> Built as a Database Systems course project demonstrating relational database design, Django ORM, multi-role authentication, and full-stack web development.

