import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from recommender.models import User

admin = User.objects.filter(username='admin').first()
if admin:
    admin.set_password('1234')
    admin.save()
    print('Admin password set to 1234')
else:
    print('Admin user not found')
