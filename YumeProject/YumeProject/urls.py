"""
URL configuration for YumeProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('hotels/', include('hotels.urls', namespace='hotels')),
    path('hotel-owner/', include('hotel_owner.urls', namespace='hotel_owner')),
    path('booking/', include('booking.urls', namespace='booking')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('qr-code/', include('qr_code.urls', namespace='qr_code')),
    path('administration/', include('administration.urls', namespace='administration')),
     ] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)