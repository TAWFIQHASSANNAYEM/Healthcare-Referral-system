from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
import os

from .models import User, GPProfile, Hospital, Referral
from .referral_model import (
    referral_model,
    get_location_from_upazila,
    DEPT_MAP
)
from .utils import download_referral_pdf

# ======================================================
# UTILITY FUNCTIONS
# ======================================================

def get_departments():
    """Get department choices for forms"""
    return [
        ('medicine', 'Medicine'),
        ('cardiology', 'Cardiology'),
        ('neurology', 'Neurology'),
        ('gastroenterology', 'Gastroenterology'),
        ('pulmonology', 'Pulmonology'),
        ('nephrology', 'Nephrology'),
        ('orthopedics', 'Orthopedics'),
        ('surgery', 'Surgery'),
        ('ent', 'ENT'),
        ('obgyn', 'Obstetrics & Gynecology'),
        ('pediatrics', 'Pediatrics'),
        ('dermatology', 'Dermatology'),
        ('ophthalmology', 'Ophthalmology'),
        ('psychiatry', 'Psychiatry'),
    ]

# ======================================================
# PUBLIC VIEWS
# ======================================================

@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'gp':
        return redirect('gp_dashboard')
    elif request.user.role == 'hospital':
        return redirect('hospital_dashboard')
    else:
        return redirect('guest_search')

def home(request):
    """Home page for all users"""
    context = {
        'hospital_count': Hospital.objects.filter(approval_status='approved').count(),
        'gp_count': GPProfile.objects.filter(approval_status='approved').count(),
        'referral_count': Referral.objects.count(),
        'district_count': Hospital.objects.filter(approval_status='approved').values('district').distinct().count(),
    }
    return render(request, 'recommender/home.html', context)

def register(request):
    """User registration selection page"""
    return render(request, 'recommender/register.html')

def gp_register(request):
    """GP registration"""
    if request.method == 'POST':
        # Get basic user data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # GP specific data
        license_number = request.POST.get('license_number')
        specialization = request.POST.get('specialization')
        assigned_upazila = request.POST.get('assigned_upazila')
        assigned_district = request.POST.get('assigned_district')

        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('gp_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('gp_register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('gp_register')

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=address,
                role='gp'
            )

            # Create GP profile
            GPProfile.objects.create(
                user=user,
                license_number=license_number,
                specialization=specialization,
                assigned_upazila=assigned_upazila,
                assigned_district=assigned_district,
            )

            messages.success(request, 'GP registration successful! Please wait for admin approval.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('gp_register')

    return render(request, 'recommender/gp_register.html')

def hospital_register(request):
    """Hospital registration"""
    if request.method == 'POST':
        # Get basic user data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Hospital specific data
        hospital_name = request.POST.get('hospital_name')
        division = request.POST.get('division')
        district = request.POST.get('district')
        upazila = request.POST.get('upazila')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        website = request.POST.get('website')
        total_beds = request.POST.get('total_beds')
        vacant_beds = request.POST.get('vacant_beds')
        icu_beds = request.POST.get('icu_beds')
        available_icu_beds = request.POST.get('available_icu_beds')
        accepting_referrals = request.POST.get('accepting_referrals') == 'on'
        has_emergency = request.POST.get('has_emergency') == 'on'
        emergency_level = request.POST.get('emergency_level', 0)

        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('hospital_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('hospital_register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('hospital_register')

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=hospital_name,  # Use hospital name as first name
                phone=phone,
                address=address,
                role='hospital'
            )

            # Map department checkboxes to boolean fields
            dept_data = {}
            for dept_code, _ in get_departments():
                dept_data[f'dept_{dept_code}'] = request.POST.get(f'dept_{dept_code}') == 'on'

            # Create hospital profile
            Hospital.objects.create(
                user=user,
                name=hospital_name,
                division=division,
                district=district,
                upazila=upazila,
                latitude=float(latitude or 0),
                longitude=float(longitude or 0),
                phone=phone,
                email=email,
                website=website,
                total_beds=int(total_beds or 0),
                vacant_beds=int(vacant_beds or 0),
                icu_beds=int(icu_beds or 0),
                available_icu_beds=int(available_icu_beds or 0),
                accepting_referrals=accepting_referrals,
                has_emergency=has_emergency,
                emergency_level=int(emergency_level or 0),
                **dept_data
            )

            messages.success(request, 'Hospital registration successful! Please wait for admin approval.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('hospital_register')

    context = {
        'departments': get_departments(),
    }
    return render(request, 'recommender/hospital_register.html', context)

def guest_search(request):
    """Public hospital search"""
    results = None
    error = None
    departments = get_departments()

    if request.method == "POST":
        department = request.POST.get("department")
        upazila = request.POST.get("upazila")
        emergency_level = int(request.POST.get("emergency_level", 0))

        patient_lat, patient_lon = get_location_from_upazila(upazila)

        if patient_lat is None:
            error = f"No hospital data found for upazila: {upazila}"
        else:
            results = referral_model(
                department=department,
                patient_lat=patient_lat,
                patient_lon=patient_lon,
                emergency_level_required=emergency_level
            )

            if not results:
                error = "No suitable hospitals found within safe distance."

    return render(request, "recommender/guest_search.html", {
        "departments": departments,
        "results": results,
        "error": error
    })

# ======================================================
# AUTHENTICATION VIEWS
# ======================================================

def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'recommender/login.html')

@login_required
def logout_view(request):
    """User logout"""
    logout_view(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# ======================================================
# ADMIN VIEWS
# ======================================================

@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')

    context = {
        'hospital_count': Hospital.objects.filter(approval_status='approved').count(),
        'gp_count': GPProfile.objects.filter(approval_status='approved').count(),
        'referral_count': Referral.objects.count(),
        'pending_count': (
            GPProfile.objects.filter(approval_status='pending').count() +
            Hospital.objects.filter(approval_status='pending').count()
        ),
        'recent_registrations': list(GPProfile.objects.filter(
            approval_status='pending'
        ).select_related('user')[:5]) + list(Hospital.objects.filter(
            approval_status='pending'
        ).select_related('user')[:5]),
        'recent_referrals': Referral.objects.select_related(
            'gp', 'hospital'
        ).order_by('-created_at')[:5],
        'active_users': User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count(),
        'this_month_referrals': Referral.objects.filter(
            created_at__gte=timezone.now().replace(day=1)
        ).count(),
    }
    return render(request, 'recommender/admin_dashboard.html', context)

@login_required
def admin_pending_approvals(request):
    """Admin pending approvals"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')

    pending_gps = GPProfile.objects.filter(approval_status='pending').select_related('user')
    pending_hospitals = Hospital.objects.filter(approval_status='pending').select_related('user')

    return render(request, 'recommender/admin_pending.html', {
        'pending_gps': pending_gps,
        'pending_hospitals': pending_hospitals,
    })

@login_required
def approve_user(request, user_id):
    """Approve user registration"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')

    user = get_object_or_404(User, id=user_id)

    if user.role == 'gp':
        profile = get_object_or_404(GPProfile, user=user)
        profile.approval_status = 'approved'
        profile.approved_at = timezone.now()
        profile.approved_by = request.user
        profile.save()
    elif user.role == 'hospital':
        profile = get_object_or_404(Hospital, user=user)
        profile.approval_status = 'approved'
        profile.approved_at = timezone.now()
        profile.approved_by = request.user
        profile.save()

    messages.success(request, f'{user.get_full_name()} has been approved.')
    return redirect('admin_pending_approvals')

@login_required
def admin_hospitals(request):
    """Admin hospital management"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')

    hospitals = Hospital.objects.all().select_related('user')
    return render(request, 'recommender/admin_hospitals.html', {'hospitals': hospitals})

@login_required
def admin_gps(request):
    """Admin GP management"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')

    gps = GPProfile.objects.all().select_related('user')
    return render(request, 'recommender/admin_gps.html', {'gps': gps})

@login_required
def admin_referrals(request):
    """Admin referral management"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')

    referrals = Referral.objects.all().select_related('gp', 'hospital').order_by('-created_at')
    return render(request, 'recommender/admin_referrals.html', {'referrals': referrals})

# ======================================================
# GP VIEWS
# ======================================================

@login_required
def gp_dashboard(request):
    """GP dashboard"""
    if request.user.role != 'gp':
        messages.error(request, 'Access denied.')
        return redirect('home')

    gp_profile = request.user.gp_profile
    referrals = Referral.objects.filter(gp=request.user)

    context = {
        'referral_count': referrals.count(),
        'this_month_count': referrals.filter(
            created_at__gte=timezone.now().replace(day=1)
        ).count(),
        'unique_hospitals': referrals.values('hospital').distinct().count(),
        'recent_referrals': referrals.select_related('hospital').order_by('-created_at')[:5],
    }
    return render(request, 'recommender/gp_dashboard.html', context)

@login_required
def gp_search_hospitals(request):
    """GP hospital search"""
    if request.user.role != 'gp':
        messages.error(request, 'Access denied.')
        return redirect('home')

    results = None
    error = None
    departments = get_departments()

    if request.method == "POST":
        department = request.POST.get("department")
        upazila = request.POST.get("upazila")
        emergency_level = int(request.POST.get("emergency_level", 0))

        patient_lat, patient_lon = get_location_from_upazila(upazila)

        if patient_lat is None:
            error = f"No hospital data found for upazila: {upazila}"
        else:
            results = referral_model(
                department=department,
                patient_lat=patient_lat,
                patient_lon=patient_lon,
                emergency_level_required=emergency_level
            )

            if not results:
                error = "No suitable hospitals found within safe distance."

    return render(request, "recommender/gp_search.html", {
        "departments": departments,
        "results": results,
        "error": error
    })

@login_required
def create_referral(request):
    """Create referral"""
    if request.user.role != 'gp':
        messages.error(request, 'Access denied.')
        return redirect('home')

    if request.method == 'POST':
        hospital_id = request.POST.get('hospital_id')
        patient_name = request.POST.get('patient_name')
        patient_age = request.POST.get('patient_age')
        patient_problem = request.POST.get('patient_problem')
        department = request.POST.get('department')
        emergency_level = int(request.POST.get('emergency_level', 0))
        upazila = request.POST.get('upazila')
        district = request.POST.get('district')

        hospital = get_object_or_404(Hospital, id=hospital_id)

        Referral.objects.create(
            gp=request.user,
            hospital=hospital,
            patient_name=patient_name,
            patient_age=patient_age,
            patient_problem=patient_problem,
            department=department,
            emergency_level=emergency_level,
            patient_upazila=upazila,
            patient_district=district,
        )

        messages.success(request, 'Referral created successfully!')
        return redirect('gp_dashboard')

    # If GET request, show form
    hospital_id = request.GET.get('hospital')
    if hospital_id:
        hospital = get_object_or_404(Hospital, id=hospital_id)
        return render(request, 'recommender/create_referral.html', {
            'hospital': hospital,
            'departments': get_departments(),
        })

    return redirect('gp_search_hospitals')

@login_required
def gp_referral_history(request):
    """GP referral history"""
    if request.user.role != 'gp':
        messages.error(request, 'Access denied.')
        return redirect('home')

    referrals = Referral.objects.filter(gp=request.user).select_related('hospital').order_by('-created_at')
    return render(request, 'recommender/gp_referrals.html', {'referrals': referrals})

@login_required
def referral_detail(request, referral_id):
    """Referral detail view"""
    referral = get_object_or_404(Referral, id=referral_id)

    # Check permissions
    if request.user.role == 'gp' and referral.gp != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    elif request.user.role == 'hospital' and referral.hospital.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    elif request.user.role not in ['gp', 'hospital', 'admin']:
        messages.error(request, 'Access denied.')
        return redirect('home')

    return render(request, 'recommender/referral_detail.html', {'referral': referral})

# ======================================================
# HOSPITAL VIEWS
# ======================================================

@login_required
def hospital_dashboard(request):
    """Hospital dashboard"""
    if request.user.role != 'hospital':
        messages.error(request, 'Access denied.')
        return redirect('home')

    hospital = request.user.hospital_profile
    referrals = Referral.objects.filter(hospital=hospital)

    context = {
        'hospital': hospital,
        'total_referrals': referrals.count(),
        'this_month_referrals': referrals.filter(
            created_at__gte=timezone.now().replace(day=1)
        ).count(),
        'recent_referrals': referrals.select_related('gp').order_by('-created_at')[:5],
    }
    return render(request, 'recommender/hospital_dashboard.html', context)

@login_required
def update_hospital(request):
    """Update hospital information"""
    if request.user.role != 'hospital':
        messages.error(request, 'Access denied.')
        return redirect('home')

    hospital = request.user.hospital_profile

    if request.method == 'POST':
        # Update hospital fields
        hospital.total_beds = int(request.POST.get('total_beds', hospital.total_beds))
        hospital.vacant_beds = int(request.POST.get('vacant_beds', hospital.vacant_beds))
        hospital.icu_beds = int(request.POST.get('icu_beds', hospital.icu_beds))
        hospital.available_icu_beds = int(request.POST.get('available_icu_beds', hospital.available_icu_beds))
        hospital.accepting_referrals = request.POST.get('accepting_referrals') == 'on'
        hospital.has_emergency = request.POST.get('has_emergency') == 'on'
        hospital.emergency_level = int(request.POST.get('emergency_level', hospital.emergency_level))

        # Update departments
        for dept_code, _ in get_departments():
            setattr(hospital, f'dept_{dept_code}', request.POST.get(f'dept_{dept_code}') == 'on')

        hospital.save()
        messages.success(request, 'Hospital information updated successfully!')
        return redirect('hospital_dashboard')

    return render(request, 'recommender/update_hospital.html', {
        'hospital': hospital,
        'departments': get_departments(),
    })

@login_required
def hospital_referrals(request):
    """Hospital referrals view"""
    if request.user.role != 'hospital':
        messages.error(request, 'Access denied.')
        return redirect('home')

    hospital = request.user.hospital_profile
    referrals = Referral.objects.filter(hospital=hospital).select_related('gp').order_by('-created_at')
    return render(request, 'recommender/hospital_referrals.html', {'referrals': referrals})

# ======================================================
# PROFILE VIEWS
# ======================================================

@login_required
def profile(request):
    """User profile management"""
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.phone = request.POST.get('phone', request.user.phone)
        request.user.address = request.POST.get('address', request.user.address)
        request.user.save()

        if request.user.role == 'gp':
            gp_profile = request.user.gp_profile
            gp_profile.license_number = request.POST.get('license_number', gp_profile.license_number)
            gp_profile.specialization = request.POST.get('specialization', gp_profile.specialization)
            gp_profile.assigned_upazila = request.POST.get('assigned_upazila', gp_profile.assigned_upazila)
            gp_profile.assigned_district = request.POST.get('assigned_district', gp_profile.assigned_district)
            gp_profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'recommender/profile.html')

# ======================================================
# API ENDPOINT (for Postman / system use)
# ======================================================

@api_view(["POST"])
def recommend_hospital(request):
    """
    GP Referral Recommendation API (Upazila-based)

    Expected JSON:
    {
        "department": "obgyn",
        "upazila": "Jashore Sadar",
        "emergency_level": 2
    }
    """

    data = request.data

    department = data.get("department")
    upazila = data.get("upazila")
    emergency_level = int(data.get("emergency_level", 0))

    patient_lat, patient_lon = get_location_from_upazila(upazila)

    if patient_lat is None:
        return Response(
            {"error": "Invalid or unknown upazila"},
            status=400
        )

    result = referral_model(
        department=department,
        patient_lat=patient_lat,
        patient_lon=patient_lon,
        emergency_level_required=emergency_level
    )

    return Response(result)
