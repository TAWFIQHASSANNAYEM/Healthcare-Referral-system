from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # API endpoints
    path("api/recommend/", views.recommend_hospital, name="recommend_hospital"),

    # Main pages
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("register/gp/", views.gp_register, name="gp_register"),
    path("register/hospital/", views.hospital_register, name="hospital_register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Guest access
    path("search/", views.guest_search, name="guest_search"),

    # Admin URLs
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/pending/", views.admin_pending_approvals, name="admin_pending_approvals"),
    path("admin/hospitals/", views.admin_hospitals, name="admin_hospitals"),
    path("admin/gps/", views.admin_gps, name="admin_gps"),
    path("admin/referrals/", views.admin_referrals, name="admin_referrals"),
    path("admin/approve/<int:user_id>/", views.approve_user, name="approve_user"),

    # GP URLs
    path("gp/dashboard/", views.gp_dashboard, name="gp_dashboard"),
    path("gp/search/", views.gp_search_hospitals, name="gp_search_hospitals"),
    path("gp/referral/create/", views.create_referral, name="create_referral"),
    path("gp/referrals/", views.gp_referral_history, name="gp_referral_history"),
    path("gp/referral/<int:referral_id>/", views.referral_detail, name="referral_detail"),

    # Hospital URLs
    path("hospital/dashboard/", views.hospital_dashboard, name="hospital_dashboard"),
    path("hospital/update/", views.update_hospital, name="update_hospital"),
    path("hospital/referrals/", views.hospital_referrals, name="hospital_referrals"),

    # Profile
    path("profile/", views.profile, name="profile"),
]
