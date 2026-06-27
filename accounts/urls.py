from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-appointments/', views.admin_appointments, name='admin_appointments'),
    path('admin-appointments/update-status/<int:appt_id>/', views.admin_update_appointment_status, name='admin_update_appointment_status'),
    path('admin-doctors/', views.admin_doctors, name='admin_doctors'),
    path('admin-patients/', views.admin_patients, name='admin_patients'),
    path('admin-patients/view/<int:patient_id>/', views.admin_view_patient, name='admin_view_patient'),
    path('admin-patients/delete/<int:patient_id>/', views.admin_delete_patient, name='admin_delete_patient'),
    path('admin-departments/', views.admin_departments, name='admin_departments'),
    path('admin-doctors/delete/<int:doctor_id>/', views.admin_delete_doctor, name='admin_delete_doctor'),
    path('admin-departments/add/', views.admin_add_department, name='admin_add_department'),
    path('admin-departments/edit/<int:dept_id>/', views.admin_edit_department, name='admin_edit_department'),
    path('admin-departments/delete/<int:dept_id>/', views.admin_delete_department, name='admin_delete_department'),
    path('admin-services/', views.admin_services, name='admin_services'),
    path('admin-services/add/', views.admin_add_service, name='admin_add_service'),
    path('admin-services/edit/<int:service_id>/', views.admin_edit_service, name='admin_edit_service'),
    path('admin-services/delete/<int:service_id>/', views.admin_delete_service, name='admin_delete_service'),
]
