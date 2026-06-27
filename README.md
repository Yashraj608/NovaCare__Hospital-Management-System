# NovaCare - Hospital Management System

A comprehensive Django-based Hospital Management System designed to streamline hospital administration, patient management, doctor appointments, and pharmacy operations. The project features a modern user interface inspired by the "Mediplus" design aesthetic.

## 🌟 Features

### 👨‍⚕️ Doctor & Patient Management
* Complete profiles for doctors and patients.
* Patient medical history tracking.
* Doctor consultation records including diagnoses, prescriptions, and test reports.

### 📅 Appointment System
* Easy scheduling of doctor appointments for patients.
* Doctor dashboard to view, accept, and manage upcoming appointments.
* Seamless workflow for consultation documentation directly from the appointment view.

### 💊 Pharmacy Module
* Integrated pharmacy system with a comprehensive database of medicines.
* Search functionality for available medicines, formulas, and usage instructions.
* Cart system for purchasing medicines directly through the platform.

### 📊 Admin Dashboard
* Custom, professional-grade administrative dashboard.
* Full CRUD (Create, Read, Update, Delete) functionality for doctors, patients, departments, and medicines.
* Real-time database integration and dynamic data visualization.

### 🔐 Accounts & Authentication
* Secure login and registration for Patients, Doctors, and Administrators.
* Role-based access control ensuring users only see what they are authorized to see.

## 🛠️ Technology Stack
* **Backend:** Python, Django
* **Database:** SQLite (default)
* **Frontend:** HTML5, CSS3, JavaScript (Mediplus UI Theme)

## 🚀 Installation & Setup

Follow these steps to run the project locally on your machine:

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd "DB project"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   * On Windows:
     ```bash
     venv\Scripts\activate
     ```
   * On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install required dependencies:**
   *(Assuming there is a requirements.txt file. If not, make sure django and other required packages are installed)*
   ```bash
   pip install -r requirements.txt
   # OR pip install django pillow etc.
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (Admin):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   Open your web browser and navigate to `http://127.0.0.1:8000/`

## 📁 Project Structure

* `accounts/` - User authentication and role management.
* `appointments/` - Managing doctor-patient bookings and consultation records.
* `core/` - Main landing pages and base configurations.
* `pharmacy/` - Medicine inventory and cart system.
* `hospital_project/` - Main Django project configuration settings.
* `templates/` - HTML templates structured by app.
* `static/` - CSS, JS, and image assets.

## 🔑 Demo Accounts

To explore the different features of the application, you can use the following demo accounts (assuming they are pre-loaded in your database or you can create them with these credentials):

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin` |
| **Doctor** | `dr_akshay` | `1234` |
| **Pharmacist** | `pharmacist` | `pass1234` |
| **Patient** | `raj` | `1234` |

---

**Developed by Yash Raj**
