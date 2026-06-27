from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book'),
    path('approve/<int:appointment_id>/', views.approve_appointment, name='approve'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel'),
    path('add_notes/<int:appointment_id>/', views.add_consultation_notes, name='add_notes'),
    path('patient_history/<int:patient_id>/', views.patient_medical_history, name='patient_history'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
]
