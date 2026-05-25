"""
Management command to create popular medical specialties
"""
from django.core.management.base import BaseCommand
from doctors.models import Specialty


class Command(BaseCommand):
    help = 'Create popular medical specialties'

    def handle(self, *args, **options):
        specialties_data = [
            {
                'name': 'Cardiologist',
                'name_bn': 'কার্ডিওলজিস্ট',
                'description': 'Heart and cardiovascular system specialist',
                'color': '#FF0000',
            },
            {
                'name': 'Pediatrician',
                'name_bn': 'শিশু বিশেষজ্ঞ',
                'description': 'Children and infant health specialist',
                'color': '#FFB6C1',
            },
            {
                'name': 'Ophthalmologist',
                'name_bn': 'নেত্র বিশেষজ্ঞ',
                'description': 'Eye and vision care specialist',
                'color': '#4169E1',
            },
            {
                'name': 'Orthopedic',
                'name_bn': 'অর্থোপেডিক',
                'description': 'Bone and Joint specialist',
                'color': '#8B4513',
            },
            {
                'name': 'Neurologist',
                'name_bn': 'নিউরোলজিস্ট',
                'description': 'Brain and nervous system specialist',
                'color': '#FFD700',
            },
            {
                'name': 'Dermatologist',
                'name_bn': 'ত্বক বিশেষজ্ঞ',
                'description': 'Skin and dermatology specialist',
                'color': '#FF69B4',
            },
            {
                'name': 'Medicine Specialist',
                'name_bn': 'মেডিসিন বিশেষজ্ঞ',
                'description': 'Internal medicine and general health',
                'color': '#228B22',
            },
            {
                'name': 'Gynecologist',
                'name_bn': 'গাইনোকোলজিস্ট',
                'description': 'Women health and reproductive specialist',
                'color': '#FF1493',
            },
        ]

        created_count = 0
        for specialty_data in specialties_data:
            specialty, created = Specialty.objects.get_or_create(
                name=specialty_data['name'],
                defaults={
                    'name_bn': specialty_data['name_bn'],
                    'description': specialty_data['description'],
                    'color': specialty_data['color'],
                    'is_active': True,
                    'order': created_count,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created specialty: {specialty.name}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'⊘ Already exists: {specialty.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully created {created_count} specialties!')
        )
