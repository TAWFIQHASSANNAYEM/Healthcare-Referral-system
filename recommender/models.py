from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# User roles
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('gp', 'General Practitioner'),
    ('hospital', 'Hospital'),
    ('guest', 'Guest'),
]

APPROVAL_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

# Custom User Model
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    # Override groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='recommender_user_set',
        related_query_name='recommender_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='recommender_user_set',
        related_query_name='recommender_user',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# GP Profile Model
class GPProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gp_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100, blank=True)
    assigned_upazila = models.CharField(max_length=100, blank=True)
    assigned_district = models.CharField(max_length=100, blank=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_gps')

    def __str__(self):
        return f"GP: {self.user.get_full_name()} - {self.approval_status}"

# Hospital Model (replacing CSV data)
class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=200)
    division = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    # Capacity
    total_beds = models.PositiveIntegerField(default=0)
    vacant_beds = models.PositiveIntegerField(default=0)
    icu_beds = models.PositiveIntegerField(default=0)
    available_icu_beds = models.PositiveIntegerField(default=0)

    # Services
    accepting_referrals = models.BooleanField(default=True)
    has_emergency = models.BooleanField(default=False)
    emergency_level = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(3)])

    # Departments (dynamic)
    dept_medicine = models.BooleanField(default=False)
    dept_cardiology = models.BooleanField(default=False)
    dept_neurology = models.BooleanField(default=False)
    dept_gastroenterology = models.BooleanField(default=False)
    dept_pulmonology = models.BooleanField(default=False)
    dept_nephrology = models.BooleanField(default=False)
    dept_orthopedics = models.BooleanField(default=False)
    dept_surgery = models.BooleanField(default=False)
    dept_ent = models.BooleanField(default=False)
    dept_obgyn = models.BooleanField(default=False)
    dept_pediatrics = models.BooleanField(default=False)
    dept_dermatology = models.BooleanField(default=False)
    dept_ophthalmology = models.BooleanField(default=False)
    dept_psychiatry = models.BooleanField(default=False)

    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_hospitals')

    def __str__(self):
        return f"{self.name} - {self.district}"

# Referral Model
class Referral(models.Model):
    gp = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_made')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='referrals_received')

    # Patient Details
    patient_name = models.CharField(max_length=100)
    patient_age = models.PositiveIntegerField()
    patient_problem = models.TextField()

    # Referral Details
    department = models.CharField(max_length=50)
    emergency_level = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(3)])
    patient_upazila = models.CharField(max_length=100)
    patient_district = models.CharField(max_length=100)

    # AI Recommendation (optional)
    ai_recommended_hospital = models.CharField(max_length=200, blank=True)
    ai_score = models.FloatField(null=True, blank=True)
    ai_reason = models.TextField(blank=True)

    # Override (if GP chose different hospital)
    override_reason = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Referral: {self.patient_name} by {self.gp.get_full_name()} to {self.hospital.name}"
