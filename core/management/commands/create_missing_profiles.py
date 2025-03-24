from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile
from django.db import transaction

class Command(BaseCommand):
    help = 'Create UserProfile objects for users that do not have them'

    def handle(self, *args, **options):
        users_without_profile = []
        total_created = 0

        # Find users without profiles
        for user in User.objects.all():
            try:
                user.userprofile
            except UserProfile.DoesNotExist:
                users_without_profile.append(user)

        if not users_without_profile:
            self.stdout.write(self.style.SUCCESS('All users have profiles!'))
            return

        # Create missing profiles
        with transaction.atomic():
            for user in users_without_profile:
                UserProfile.objects.create(user=user)
                total_created += 1
                self.stdout.write(f'Created profile for user: {user.username}')

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {total_created} user profiles!'
        )) 