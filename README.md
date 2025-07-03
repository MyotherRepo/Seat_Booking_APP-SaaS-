# 🪑 Hybrid Workplace Seat Booking System

A flexible **seat reservation and attendance system** for hybrid workplaces — built with **Django** (REST API backend) and **React** (frontend). Supports real-time seat booking, waitlisting, attendance marking, analytics, and multi-org (SaaS) architecture.

---

## 🧠 Assumptions

- 🧑 Employees must book seats before visiting the office.
- 📍 Floor plans and seat locations are pre-defined by **management**.
- 📅 Employees can **view availability** on a given date via a floor plan UI.
- 🔒 Users must **mark attendance** on arrival — unmarked seats by 10:00 AM are freed.
- 🔁 Cancelled or no-show seats are **auto-assigned to waitlisted users**.
- 🏢 Multiple organizations can use the platform, each operating in its own namespace.

---

## 🔄 General Flow

### 🧑 Employee

1. **Login** → Token Auth
2. **View Floor Plan** → Clickable UI
3. **Book Seat** → If full, option to waitlist
4. **Mark Attendance** on arrival
5. **Cancel Booking** → Frees seat + auto-promotes waitlisted user

### 👩‍💼 Management

1. **Create Floor Plans / Seats**
2. **Book for Others or Maintenance**
3. **View Reports**:
   - Booked vs Attended
   - No-shows
   - Utilization % by floor
4. **Cancel Bookings / Free Seats**
5. **Handle Multiple Orgs** (SaaS context)

---

## 📊 ER Diagram
![ER Diagram](docs/ER_Diagram_Hybrid_Seat_Booking.png)

---

## 🧪 Key API Highlights
POST /api/login/ → Get token

GET /api/seats/available/?date=2025-07-01 → Available seats for a date

POST /api/bookings/ → Book a seat

POST /api/waitlist/ → Join waitlist

POST /api/attendance/mark/ → Mark presence

DELETE /api/bookings/cancel/<id>/ → Cancel booking

## 🧱 Tech Stack

| Layer      | Tech                    |
|------------|-------------------------|
| Backend    | Django + DRF            |
| Frontend   | React + Axios           |
| DB         | MongoDB   |
| Auth       | Token-based             |
| Scheduling | Django Commands (or Celery) |
| Multi-Tenant | Org-based data isolation |

---


## ⚙️ Setup

### 🔧 Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


