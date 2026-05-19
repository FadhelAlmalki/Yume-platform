from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import City, CapsuleHotel, Capsule


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'image', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    fieldsets = (
        (None, {'fields': ('name', 'image')}),
        ('Status', {'fields': ('is_active',)}),
    )


@admin.register(CapsuleHotel)
class CapsuleHotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel_owner', 'city', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'address']
    list_editable = ['is_active']


@admin.register(Capsule)
class CapsuleAdmin(admin.ModelAdmin):
    list_display = ['capsule_num', 'hotel', 'hour_price', 'night_price', 'is_available']
    list_filter = ['is_available', 'hotel']
    search_fields = ['capsule_num']

# admin.register.site(City,CityAdmin)