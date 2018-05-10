from django.core.management.base import BaseCommand, CommandError
from user.models import PassRecQuestions

class Command(BaseCommand):
    help = 'Loads the default settings into the database. The settings include registration security questions.'

    def handle(self, *args, **options):
        try:
            q, created = PassRecQuestions.objects.get_or_create(question='What food you do not like?')
            if created: q.save()

            q, created = PassRecQuestions.objects.get_or_create(question='What is the name of your pet?')
            if created: q.save()

            q, created = PassRecQuestions.objects.get_or_create(question='What is (was) your nickname?')
            if created: q.save()

            q, created = PassRecQuestions.objects.get_or_create(question='What is your favorite movie or cartoon?')
            if created: q.save()

            q, created = PassRecQuestions.objects.get_or_create(question='On what street do you live?')
            if created: q.save()

        except:
            raise CommandError('The database is probably not connected, make sure that you connected PostgreSQL in the settings.py. Also, you may need to run "python manage.py migrate" command before setdefaults command.')

        self.stdout.write(self.style.SUCCESS('Successfully added all default settings.'))
