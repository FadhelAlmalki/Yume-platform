from django.db import models

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='cities/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CapsuleHotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=300)
    image = models.ImageField(upload_to='hotels/')
    rating = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    hotel_owner = models.ForeignKey(
        'accounts.OwnerProfile',
        on_delete=models.CASCADE,
        related_name='hotels'
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        null=True,
        related_name='hotels'
    )

    def __str__(self):
        return self.name


class HotelImage(models.Model):
    hotel = models.ForeignKey(
        CapsuleHotel,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='hotels/gallery/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.hotel.name} - image {self.pk}"


class Capsule(models.Model):
    hour_price = models.DecimalField(max_digits=8, decimal_places=2)
    night_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)
    capsule_num = models.CharField(max_length=50, unique=True)

    hotel = models.ForeignKey(
        CapsuleHotel,
        on_delete=models.CASCADE,
        related_name='capsules'
    )

    def __str__(self):
        return f"{self.hotel.name} - {self.capsule_num}"
