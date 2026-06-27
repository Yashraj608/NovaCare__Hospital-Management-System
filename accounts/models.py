from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_receptionist = models.BooleanField(default=False)
    is_pharmacist = models.BooleanField(default=False)


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='departments/icons/', blank=True, null=True)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    availability = models.CharField(max_length=255, help_text="e.g., Mon-Fri, 9AM-5PM", blank=True)
    profile_picture = models.ImageField(upload_to='doctors/profiles/', blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} - {self.department}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"

class Pharmacist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pharmacist_profile')
    experience_years = models.PositiveIntegerField(default=0)
    profile_picture = models.ImageField(upload_to='pharmacists/profiles/', blank=True, null=True)

    def __str__(self):
        return f"Pharmacist: {self.user.get_full_name() or self.user.username}"
