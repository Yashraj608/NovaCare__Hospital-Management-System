from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(help_text="Detailed description of the service (e.g. MRI, X-Ray, Blood Test)")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Cost of the service")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
