# NovaCare - Hospital Management System

NovaCare is a Django-based hospital management system that supports patient management, doctor appointments, pharmacy operations, and admin workflows.

## Features

- Doctor and patient management
- Appointment booking and medical history
- Pharmacy inventory and billing
- Admin dashboard for departments, services, doctors, and patients
- User authentication and role-based access

## Tech Stack

- Python
- Django
- SQLite
- HTML, CSS, JavaScript

## Setup Instructions

1. Clone the repository
   ```bash
   git clone https://github.com/Yashraj608/NovaCare__Hospital-Management-System.git
   cd NovaCare__Hospital-Management-System
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install django pillow
   ```

4. Apply migrations
   ```bash
   python manage.py migrate
   ```

5. Create a superuser
   ```bash
   python manage.py createsuperuser
   ```

6. Run the server
   ```bash
   python manage.py runserver
   ```

7. Open the app in browser
   ```text
   http://127.0.0.1:8000/
   ```

## Project Structure

- accounts/ - authentication and user roles
- appointments/ - booking and appointment management
- core/ - homepage and general site pages
- pharmacy/ - medicines, cart, billing
- templates/ - HTML templates
- static/ - CSS, JS, and images
- hospital_project/ - Django project settings

## Notes

- The project uses SQLite by default.
- Media files and uploaded images are stored in the media/ folder.

## Author

Yash Raj
