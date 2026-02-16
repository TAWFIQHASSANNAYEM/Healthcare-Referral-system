from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from django.http import HttpResponse

def generate_referral_pdf(referral):
    """
    Generate PDF referral slip for a referral
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )

    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8
    )

    story = []

    # Title
    story.append(Paragraph("MEDICAL REFERRAL SLIP", title_style))
    story.append(Spacer(1, 12))

    # Referral Information
    story.append(Paragraph("REFERRAL DETAILS", header_style))

    referral_data = [
        ["Referral ID:", f"REF-{referral.id:06d}"],
        ["Date:", referral.created_at.strftime("%B %d, %Y %H:%M")],
        ["Urgency Level:", f"Level {referral.emergency_level}" if referral.emergency_level > 0 else "Non-emergency"],
    ]

    referral_table = Table(referral_data, colWidths=[2*inch, 4*inch])
    referral_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(referral_table)
    story.append(Spacer(1, 12))

    # Patient Information
    story.append(Paragraph("PATIENT INFORMATION", header_style))

    patient_data = [
        ["Patient Name:", referral.patient_name],
        ["Age:", str(referral.patient_age)],
        ["Location:", f"{referral.patient_upazila}, {referral.patient_district}"],
        ["Presenting Problem:", referral.patient_problem],
        ["Department:", referral.get_department_display()],
    ]

    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 12))

    # Referring GP Information
    story.append(Paragraph("REFERRING PHYSICIAN", header_style))

    gp_data = [
        ["Name:", referral.gp.get_full_name()],
        ["License Number:", referral.gp.gp_profile.license_number],
        ["Specialization:", referral.gp.gp_profile.specialization or "General Practice"],
        ["Assigned Area:", f"{referral.gp.gp_profile.assigned_upazila}, {referral.gp.gp_profile.assigned_district}"],
    ]

    gp_table = Table(gp_data, colWidths=[2*inch, 4*inch])
    gp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(gp_table)
    story.append(Spacer(1, 12))

    # Receiving Hospital Information
    story.append(Paragraph("RECEIVING HOSPITAL", header_style))

    hospital_data = [
        ["Hospital Name:", referral.hospital.name],
        ["Location:", f"{referral.hospital.upazila}, {referral.hospital.district}"],
        ["Phone:", referral.hospital.phone or "Not available"],
        ["Email:", referral.hospital.email or "Not available"],
    ]

    hospital_table = Table(hospital_data, colWidths=[2*inch, 4*inch])
    hospital_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(hospital_table)
    story.append(Spacer(1, 12))

    # Footer
    story.append(Paragraph("This referral slip should be presented at the receiving hospital.", content_style))
    story.append(Paragraph("For urgent cases, please contact the hospital directly.", content_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

def download_referral_pdf(request, referral_id):
    """
    View to download referral PDF
    """
    from .models import Referral
    from django.shortcuts import get_object_or_404

    referral = get_object_or_404(Referral, id=referral_id)

    # Check permissions
    if request.user.role == 'gp' and referral.gp != request.user:
        from django.contrib import messages
        messages.error(request, 'Access denied.')
        from django.shortcuts import redirect
        return redirect('home')
    elif request.user.role == 'hospital' and referral.hospital.user != request.user:
        from django.contrib import messages
        messages.error(request, 'Access denied.')
        from django.shortcuts import redirect
        return redirect('home')
    elif request.user.role not in ['gp', 'hospital', 'admin']:
        from django.contrib import messages
        messages.error(request, 'Access denied.')
        from django.shortcuts import redirect
        return redirect('home')

    buffer = generate_referral_pdf(referral)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="referral_{referral.id}.pdf"'

    return response
