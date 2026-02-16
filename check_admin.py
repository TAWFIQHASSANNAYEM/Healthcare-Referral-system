import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from recommender.models import User

admin = User.objects.filter(username='admin').first()
if admin:
    print(f"Admin user: {admin}")
    print(f"Role: {admin.role}")
    print(f"Is superuser: {admin.is_superuser}")
else:
    print("No admin user found")
