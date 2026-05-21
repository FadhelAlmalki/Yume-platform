from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpRequest
from .models import City, CapsuleHotel, Capsule
from hotels.models import Capsule
from django.core.paginator import Paginator
from django.utils import timezone
from booking.models import Booking
from reviews.models import Review
from datetime import timedelta

# ── City Views ──

# Customer, Guest
def city_list(request):
    cities = City.objects.filter(is_active=True)
    return render(request, 'hotels/city_list.html', {'cities': cities})


# Customer, Guest
# Customer, Guest
def hotel_list(request):

    hotels = CapsuleHotel.objects.filter(is_active=True)

    # =========================
    # SEARCH BY HOTEL NAME
    # =========================
    q = request.GET.get('q')

    if q:
        hotels = hotels.filter(name__icontains=q)

    # =========================
    # CITY FILTER
    # =========================
    city_name = request.GET.get('city')

    if city_name:
        hotels = hotels.filter(city__name__icontains=city_name)

    # ── Booking Type Filter ──
    booking_type = request.GET.get('booking_type')

    if booking_type == 'hour':
        hotels = hotels.filter(capsules__hour_price__isnull=False).distinct()

    elif booking_type == 'night':
        hotels = hotels.filter(capsules__night_price__isnull=False).distinct()
        
    # =========================
    # PRICE FILTER
    # =========================
    price = request.GET.get('price')

    if price == 'low':
        hotels = hotels.filter(
            capsules__hour_price__lt=100
        ).distinct()

    elif price == 'mid':
        hotels = hotels.filter(
            capsules__hour_price__range=(100, 300)
        ).distinct()

    elif price == 'high':
        hotels = hotels.filter(
            capsules__hour_price__gt=300
        ).distinct()

    # =========================
    # CAPSULES FILTER
    # =========================
    capsules = request.GET.get('capsules')

    if capsules:
        hotels = hotels.filter(
            capsules__is_available=True
        ).distinct()

    # =========================
    # NO HOTELS MESSAGE
    # =========================
    no_results = False

    if not hotels.exists():
        no_results = True

    # =========================
    # PAGINATION
    # =========================
    paginator = Paginator(hotels, 6)

    page_number = request.GET.get('page')

    hotels = paginator.get_page(page_number)

    # =========================
    # CITIES
    # =========================
    cities = City.objects.filter(is_active=True)

    return render(request, 'hotels/hotel_list.html', {

        'hotels': hotels,
        'cities': cities,
        'no_results': no_results,

        # keep search values
        'selected_city': request.GET.get('city', ''),
        'selected_check_in': request.GET.get('check_in', ''),
        'selected_check_out': request.GET.get('check_out', ''),
        'selected_capsules': request.GET.get('capsules', '1'),

    })


# Customer, Guest
def hotel_detail(request, pk):
    hotel = get_object_or_404(CapsuleHotel, pk=pk)
    capsules = hotel.capsules.filter(is_available=True)
    related_hotels = CapsuleHotel.objects.filter(
        city=hotel.city,
        is_active=True
    ).exclude(pk=pk)[:3]
    reviews = Review.objects.filter(hotel=hotel).select_related('user').order_by('-created_at')

    has_booked = False
    if request.user.is_authenticated:
        try:
            has_booked = Booking.objects.filter(
                customer=request.user.customer_profile,
                capsule__hotel=hotel,
                status=Booking.STATUS_PAID,
            ).exists()
        except Exception:
            has_booked = False

    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel,
        'capsules': capsules,
        'capsules_count': capsules.count(),
        'reviews': reviews,
        'has_booked': has_booked,
        'related_hotels': related_hotels,
        'check_in': request.GET.get('check_in', ''),
        'check_out': request.GET.get('check_out', ''),
        'capsules_qty': request.GET.get('capsules', 1),
    })