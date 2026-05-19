from django.db import models
from booking.models import Booking
# Create your models here.

class QRAccess(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='qr_access')
    qr_token = models.CharField(max_length=64, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/')
    is_used = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"QR for Booking {self.booking.id}"