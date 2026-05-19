from django.urls import path
from . import views

app_name = 'qr_code'

# urlpatterns = [
#     path('', views.qr_code_view, name='qr_code_view'),
# ]
urlpatterns = [
    path('booking/<int:booking_id>/', views.qr_detail, name='qr_detail'),
    path('booking/<int:booking_id>/pdf/', views.qr_pdf, name='qr_pdf'),
    path('verify/<str:token>/', views.verify_qr, name='verify_qr'),
]