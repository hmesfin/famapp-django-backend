"""
Management command to set up periodic Celery tasks.

This command configures Celery Beat periodic tasks in the database
using django_celery_beat models.
"""

import json

from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask


class Command(BaseCommand):
    help = 'Set up periodic tasks for Celery Beat'

    def handle(self, *args, **options):
        self.stdout.write('Setting up periodic tasks...')

        # Create or get the crontab schedule for 2 AM daily
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='2',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone='UTC'
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created crontab schedule: Daily at 2:00 AM UTC')
            )

        # Create or update the cleanup task
        task, created = PeriodicTask.objects.update_or_create(
            name='Cleanup Expired Invitations',
            defaults={
                'task': 'apps.users.tasks.cleanup_expired_invitations',
                'crontab': schedule,
                'enabled': True,
                'description': 'Daily cleanup of expired pending invitations at 2 AM UTC',
                'kwargs': json.dumps({}),  # No arguments needed
                'expires': None,  # Task doesn't expire
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('Created periodic task: Cleanup Expired Invitations')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Updated periodic task: Cleanup Expired Invitations')
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\nPeriodic task configured successfully!\n'
                'The cleanup_expired_invitations task will run daily at 2:00 AM UTC.\n'
                'Make sure Celery Beat is running: docker compose up celerybeat'
            )
        )