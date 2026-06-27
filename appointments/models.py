from django.db import models
from accounts.models import Patient, Doctor

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    symptoms = models.TextField(help_text="Describe the medical issue or reason for visit.")
    
    # Medical Record Fields
    disease_diagnosis = models.CharField(max_length=255, blank=True, null=True, help_text="Doctor's primary diagnosis")
    prescription = models.TextField(blank=True, null=True, help_text="Details of medicines prescribed")
    test_reports = models.TextField(blank=True, null=True, help_text="Notes on any lab tests and their fees/results")
    
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment: {self.patient} with {self.doctor} on {self.date} at {self.time}"

    class Meta:
        ordering = ['-date', '-time']
        # Ensure a patient cannot book the exact same slot twice
        unique_together = ('patient', 'doctor', 'date', 'time')

class PrescribedMedicine(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescribed_medicines')
    medicine = models.ForeignKey('pharmacy.Medicine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    dosage_instructions = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.medicine.name} for {self.appointment.patient.user.username}"
