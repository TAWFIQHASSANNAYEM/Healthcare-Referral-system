from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, GPProfile, Hospital, Referral

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'address')}),
    )

@admin.register(GPProfile)
class GPProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'specialization', 'assigned_upazila', 'assigned_district', 'approval_status')
    list_filter = ('approval_status', 'assigned_district', 'assigned_upazila')
    search_fields = ('user__username', 'user__email', 'license_number', 'specialization')
    readonly_fields = ('approved_at',)

    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Professional Details', {'fields': ('license_number', 'specialization')}),
        ('Location Assignment', {'fields': ('assigned_upazila', 'assigned_district')}),
        ('Approval Status', {'fields': ('approval_status', 'approved_at', 'approved_by')}),
    )

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'division', 'district', 'upazila', 'approval_status', 'total_beds', 'vacant_beds')
    list_filter = ('approval_status', 'division', 'district', 'has_emergency')
    search_fields = ('name', 'user__username', 'district', 'upazila')
    readonly_fields = ('approved_at',)

    fieldsets = (
        ('Basic Information', {'fields': ('user', 'name', 'division', 'district', 'upazila')}),
        ('Contact Information', {'fields': ('phone', 'email', 'website')}),
        ('Location', {'fields': ('latitude', 'longitude')}),
        ('Capacity', {'fields': ('total_beds', 'vacant_beds', 'icu_beds', 'available_icu_beds')}),
        ('Services', {'fields': ('has_emergency', 'emergency_level', 'accepting_referrals')}),
        ('Departments', {'fields': ('dept_medicine', 'dept_cardiology', 'dept_neurology', 'dept_gastroenterology',
                                   'dept_pulmonology', 'dept_nephrology', 'dept_orthopedics', 'dept_surgery',
                                   'dept_ent', 'dept_obgyn', 'dept_pediatrics', 'dept_dermatology',
                                   'dept_ophthalmology', 'dept_psychiatry')}),
        ('Approval Status', {'fields': ('approval_status', 'approved_at', 'approved_by')}),
    )

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('id', 'gp', 'hospital', 'patient_name', 'department', 'emergency_level', 'created_at')
    list_filter = ('department', 'emergency_level', 'created_at', 'hospital__district')
    search_fields = ('gp__username', 'hospital__name', 'patient_name', 'patient_problem')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Referral Information', {'fields': ('gp', 'hospital')}),
        ('Patient Details', {'fields': ('patient_name', 'patient_age', 'patient_upazila', 'patient_district', 'patient_problem')}),
        ('Medical Information', {'fields': ('department', 'emergency_level')}),
        ('AI Recommendation', {'fields': ('ai_recommended_hospital', 'ai_score', 'ai_reason'), 'classes': ('collapse',)}),
        ('Override Information', {'fields': ('override_reason',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
