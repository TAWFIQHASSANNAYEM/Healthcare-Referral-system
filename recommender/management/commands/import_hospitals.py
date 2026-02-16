from django.core.management.base import BaseCommand
import csv
from recommender.models import Hospital

class Command(BaseCommand):
    help = 'Import hospitals from CSV file'

    def handle(self, *args, **options):
        csv_file_path = 'recommender/BD_200_Hospital_Facility_Dataset - Sheet1.csv'
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Hospital.objects.get_or_create(
                    name=row['Hospital Name'],
                    defaults={
                        'location': row['Location'],
                        'district': row['District'],
                        'division': row['Division'],
                        'department': row['Department'],
                        'beds': int(row['Beds']) if row['Beds'] else 0,
                        'icu_beds': int(row['ICU Beds']) if row['ICU Beds'] else 0,
                        'emergency_services': row['Emergency Services'].lower() == 'yes',
                        'contact': row['Contact'],
                        'latitude': float(row['Latitude']) if row['Latitude'] else 0.0,
                        'longitude': float(row['Longitude']) if row['Longitude'] else 0.0,
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported hospitals from CSV'))
