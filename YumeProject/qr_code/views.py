from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
import os
import uuid
import qrcode

from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, Image as RLImage

from booking.models import Booking
from .models import QRAccess

# Create your views here.

# def qr_code_view(request):
#     return request(200)




# ── Generate QR for a booking ──
def generate_qr(booking):
    token = uuid.uuid4().hex
    token_label = f"YUME-{booking.capsule.hotel.name}-{booking.id}"

    # Generate QR image
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(token_label)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Create QRAccess object
    qr_access = QRAccess.objects.create(
        booking=booking,
        qr_token=token,
        expires_at=booking.check_out,
    )
    qr_access.qr_code.save(f"qr_{token}.png", ContentFile(buffer.read()))
    qr_access.save()

    return qr_access


# ── View QR code page ──
def qr_detail(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    qr_access = get_object_or_404(QRAccess, booking=booking)
    return render(request, 'qr_code/qr_detail.html', {
        'booking': booking,
        'qr_access': qr_access,
    })


# ── Download QR as PDF ──
# ── Download QR as PDF ──
def qr_pdf(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    qr_access = get_object_or_404(QRAccess, booking=booking)

    # ── Token format: YUME-{hotel_name}-{booking_id} ──
    token_label = f"YUME-{booking.capsule.hotel.name}-{booking.id}"

    # ── Styles ──
    title_style = ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=18, alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle('Subtitle', fontName='Helvetica', fontSize=10, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=4)
    section_style = ParagraphStyle('Section', fontName='Helvetica-Bold', fontSize=11, spaceAfter=6, spaceBefore=10)
    label_style = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=9, textColor=colors.black)
    value_style = ParagraphStyle('Value', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#333333'))
    footer_style = ParagraphStyle('Footer', fontName='Helvetica', fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
    scan_style = ParagraphStyle('Scan', fontName='Helvetica', fontSize=9, alignment=TA_CENTER, textColor=colors.grey, spaceBefore=6)
    token_style = ParagraphStyle('Token', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER, textColor=colors.black, spaceBefore=4)

    def build_row(label, value, highlight=False):
        label_p = Paragraph(label, label_style)
        value_p = Paragraph(str(value), value_style)
        t = Table([[label_p, value_p]], colWidths=[5*cm, 11*cm])
        style = [
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]
        if highlight:
            style += [
                ('BACKGROUND', (1,0), (1,0), colors.HexColor('#d4edda')),
                ('TEXTCOLOR', (1,0), (1,0), colors.HexColor('#155724')),
            ]
        t.setStyle(TableStyle(style))
        return t

    # ── Generate QR with token label ──
    qr = qrcode.QRCode(box_size=8, border=4)
    qr.add_data(token_label)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # ── Build PDF ──
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    story = []

    # Header
    story.append(Paragraph("Yume", title_style))
    story.append(Paragraph("Official Booking Confirmation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'), spaceAfter=10))
    story.append(Spacer(1, 0.5*cm))

    # Booking Information
    story.append(Paragraph("Booking Information", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd'), spaceAfter=6))
    story.append(Spacer(1, 0.2*cm))
    story.append(build_row("Booking ID:", token_label))
    story.append(build_row("Booking Status:", booking.status.capitalize(), highlight=True))
    story.append(build_row("Check-in:", booking.check_in.strftime('%d %b %Y, %H:%M')))
    story.append(build_row("Check-out:", booking.check_out.strftime('%d %b %Y, %H:%M')))
    story.append(build_row("Booking Type:", booking.booking_type.capitalize()))
    story.append(build_row("Total Price:", f"{booking.total_price} SAR"))
    story.append(Spacer(1, 0.3*cm))

    # Hotel Information
    story.append(Paragraph("Hotel Information", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd'), spaceAfter=6))
    story.append(Spacer(1, 0.2*cm))
    story.append(build_row("Hotel Name:", booking.capsule.hotel.name))
    story.append(build_row("Capsule Number:", booking.capsule.capsule_num))
    story.append(build_row("City:", booking.capsule.hotel.city.name))
    story.append(build_row("Address:", booking.capsule.hotel.address))
    story.append(Spacer(1, 0.3*cm))

    # Customer Information
    story.append(Paragraph("Customer Information", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#dddddd'), spaceAfter=6))
    story.append(Spacer(1, 0.2*cm))
    story.append(build_row("Name:", booking.customer.user.get_full_name() or booking.customer.user.username))
    story.append(build_row("Email:", booking.customer.user.email))
    story.append(Spacer(1, 0.5*cm))

    # QR Code
    story.append(Paragraph(f"Scan to verify booking: {token_label}", scan_style))
    story.append(Spacer(1, 0.3*cm))
    qr_image = RLImage(qr_buffer, width=4*cm, height=4*cm)
    qr_table = Table([[qr_image]], colWidths=[16*cm])
    qr_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(qr_table)
    story.append(Paragraph(token_label, token_style))
    story.append(Spacer(1, 0.5*cm))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc'), spaceAfter=6))
    story.append(Paragraph("This confirmation is issued by Yume Platform. Valid only for the specified booking and time period.", footer_style))
    story.append(Paragraph(f"Booking ID: {token_label}", footer_style))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{token_label}.pdf"'
    return response


# ── Verify QR (hotel side) ──
def verify_qr(request, token):
    qr_access = get_object_or_404(QRAccess, qr_token=token)

    if qr_access.is_used:
        status = 'already_used'
    elif qr_access.expires_at < timezone.now():
        status = 'expired'
    else:
        qr_access.is_used = True
        qr_access.save()
        status = 'success'

    return render(request, 'qr_code/verify.html', {
        'qr_access': qr_access,
        'status': status,
    })