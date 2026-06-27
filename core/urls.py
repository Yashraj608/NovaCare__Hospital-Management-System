from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('branches/', views.branches, name='branches'),
    path('services/', views.services, name='services'),
    path('doctors/', views.doctors, name='doctors'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('edit-doctor/<int:doctor_id>/', views.edit_doctor, name='edit_doctor'),
    path('delete-doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),
]
