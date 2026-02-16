from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import GPProfile, Hospital, Referral

User = get_user_model()

class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass',
            role='admin'
        )

        # Create GP user
        self.gp_user = User.objects.create_user(
            username='gp',
            email='gp@test.com',
            password='gppass',
            role='gp'
        )
        self.gp_profile = GPProfile.objects.create(
            user=self.gp_user,
            license_number='12345',
            specialization='General Medicine',
            assigned_upazila='Dhaka Sadar',
            assigned_district='Dhaka',
            approval_status='approved'
        )

        # Create hospital user
        self.hospital_user = User.objects.create_user(
            username='hospital',
            email='hospital@test.com',
            password='hospitalpass',
            role='hospital'
        )
        self.hospital = Hospital.objects.create(
            user=self.hospital_user,
            name='Test Hospital',
            division='Dhaka',
            district='Dhaka',
            upazila='Dhaka Sadar',
            approval_status='approved',
            total_beds=100,
            vacant_beds=50,
            icu_beds=20,
            available_icu_beds=10
        )

    def test_admin_dashboard_access(self):
        """Test admin can access dashboard"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')

    def test_admin_dashboard_denied_for_non_admin(self):
        """Test non-admin cannot access admin dashboard"""
        self.client.login(username='gp', password='gppass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_gp_dashboard_access(self):
        """Test GP can access dashboard"""
        self.client.login(username='gp', password='gppass')
        response = self.client.get(reverse('gp_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'GP Dashboard')

    def test_gp_dashboard_denied_for_non_gp(self):
        """Test non-GP cannot access GP dashboard"""
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('gp_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_hospital_dashboard_access(self):
        """Test hospital can access dashboard"""
        self.client.login(username='hospital', password='hospitalpass')
        response = self.client.get(reverse('hospital_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hospital Dashboard')

    def test_hospital_dashboard_denied_for_non_hospital(self):
        """Test non-hospital cannot access hospital dashboard"""
        self.client.login(username='gp', password='gppass')
        response = self.client.get(reverse('hospital_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_home_page_access(self):
        """Test home page is accessible without login"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Healthcare Referral System')

    def test_guest_search_access(self):
        """Test guest search is accessible without login"""
        response = self.client.get(reverse('guest_search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hospital Search')

class ReferralTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create GP user
        self.gp_user = User.objects.create_user(
            username='gp',
            email='gp@test.com',
            password='gppass',
            role='gp'
        )
        self.gp_profile = GPProfile.objects.create(
            user=self.gp_user,
            license_number='12345',
            specialization='General Medicine',
            assigned_upazila='Dhaka Sadar',
            assigned_district='Dhaka',
            approval_status='approved'
        )

        # Create hospital
        self.hospital_user = User.objects.create_user(
            username='hospital',
            email='hospital@test.com',
            password='hospitalpass',
            role='hospital'
        )
        self.hospital = Hospital.objects.create(
            user=self.hospital_user,
            name='Test Hospital',
            division='Dhaka',
            district='Dhaka',
            upazila='Dhaka Sadar',
            approval_status='approved',
            total_beds=100,
            vacant_beds=50,
            icu_beds=20,
            available_icu_beds=10
        )

    def test_create_referral(self):
        """Test GP can create referral"""
        self.client.login(username='gp', password='gppass')
        response = self.client.post(reverse('create_referral'), {
            'hospital_id': self.hospital.id,
            'patient_name': 'John Doe',
            'patient_age': 30,
            'patient_problem': 'Fever',
            'department': 'medicine',
            'emergency_level': 1,
            'upazila': 'Dhaka Sadar',
            'district': 'Dhaka'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Referral.objects.filter(gp=self.gp_user, hospital=self.hospital).exists())

    def test_referral_history_access(self):
        """Test GP can access referral history"""
        self.client.login(username='gp', password='gppass')
        response = self.client.get(reverse('gp_referral_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Referral History')

class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_gp_registration(self):
        """Test GP registration"""
        response = self.client.post(reverse('gp_register'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'email': 'john@test.com',
            'password1': 'password123',
            'password2': 'password123',
            'phone': '1234567890',
            'address': '123 Main St',
            'license_number': '12345',
            'specialization': 'General Medicine',
            'assigned_upazila': 'Dhaka Sadar',
            'assigned_district': 'Dhaka'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='johndoe').exists())
        self.assertTrue(GPProfile.objects.filter(user__username='johndoe').exists())

    def test_hospital_registration(self):
        """Test hospital registration"""
        response = self.client.post(reverse('hospital_register'), {
            'username': 'testhospital',
            'email': 'hospital@test.com',
            'password1': 'password123',
            'password2': 'password123',
            'phone': '1234567890',
            'address': '123 Hospital St',
            'hospital_name': 'Test Hospital',
            'division': 'Dhaka',
            'district': 'Dhaka',
            'upazila': 'Dhaka Sadar',
            'latitude': '23.8103',
            'longitude': '90.4125',
            'website': 'http://testhospital.com',
            'total_beds': 100,
            'vacant_beds': 50,
            'icu_beds': 20,
            'available_icu_beds': 10,
            'accepting_referrals': 'on',
            'has_emergency': 'on',
            'emergency_level': 2,
            'dept_medicine': 'on',
            'dept_cardiology': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='testhospital').exists())
        self.assertTrue(Hospital.objects.filter(user__username='testhospital').exists())
