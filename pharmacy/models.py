from django.db import models
from accounts.models import Pharmacist

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    formula = models.CharField(max_length=255, blank=True, help_text="Chemical formula or generic name")
    usage_instructions = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    requires_prescription = models.BooleanField(default=False)
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.formula}"

class PharmacyBill(models.Model):
    patient_name = models.CharField(max_length=200, blank=True, help_text="Name of the patient or OTC customer")
    pharmacist = models.ForeignKey(Pharmacist, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Bill #{self.id} for {self.patient_name} on {self.date.strftime('%Y-%m-%d')}"

class PharmacyBillItem(models.Model):
    bill = models.ForeignKey(PharmacyBill, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.medicine.name}"

from accounts.models import Patient

class PatientCart(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.patient}"

class PatientCartItem(models.Model):
    cart = models.ForeignKey(PatientCart, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.medicine.name} in {self.cart.patient}'s cart"

class UnifiedBill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='unified_bills')
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    total_medicine_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_consultation_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Unified Bill #{self.id} for {self.patient.user.username}"
