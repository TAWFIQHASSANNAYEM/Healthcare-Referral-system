# TODO: Role-Based Healthcare Referral System Implementation

## Step 1: Models Creation
- [x] Create custom User model with roles (Admin, GP, Hospital, Guest)
- [x] Create GPProfile model for GP details and approval status
- [x] Create Hospital model to replace CSV data
- [x] Create Referral model for logging referrals

## Step 2: Authentication Setup
- [ ] Update settings.py for custom user model
- [ ] Add authentication views (login, logout, registration)

## Step 3: Views Implementation
- [x] Registration views for GP and Hospital
- [x] Dashboard views for each role (Admin, GP, Hospital, Guest)
- [x] Hospital management views for Hospital users
- [x] Referral creation views for GPs
- [x] Admin approval views

## Step 4: URL Configuration
- [x] Update urls.py with new patterns for all views

## Step 5: Templates Creation
- [x] Create base templates with navigation
- [x] Create registration forms
- [x] Create dashboard templates for each role
- [x] Create hospital management forms
- [x] Create referral forms and history views

## Step 6: Admin Interface
- [x] Register all models in admin.py
- [x] Customize admin for user approvals and management

## Step 7: Data Migration
- [x] Create script to migrate CSV hospital data to database
- [x] Run migrations

## Step 8: Referral System Enhancement
- [x] Update referral_model.py to use database instead of CSV
- [x] Add patient details input
- [ ] Implement PDF referral slip generation
- [x] Add referral logging

## Step 9: Permissions and Security
- [x] Implement role-based access control
- [x] Add decorators for view permissions
- [x] Ensure GPs can only refer after approval

## Step 10: Testing and Validation
- [x] Test all user workflows
- [x] Validate referral generation
- [x] Test admin approvals
- [x] Add form validation and error handling

## Step 11: Final Completion Tasks
- [x] Add AUTH_USER_MODEL to settings.py
- [x] Add login/logout views
- [x] Create missing templates (admin_pending.html, create_referral.html, update_hospital.html, etc.)
- [x] Create hospital data import script
- [x] Add PDF generation capability
- [x] Register models in admin interface
- [ ] Test complete system functionality
