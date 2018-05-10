from django.core.management.base import BaseCommand, CommandError
from user.models import PassRecQuestions
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Loads the default settings into the database. The settings include registration security questions and creating a superuser.'

    def handle(self, *args, **options):
        # set the default superuser
        try:
            if not User.objects.filter(username="gcsuperuser").exists():
                User.objects.create_superuser("gcsuperuser", "admin@admin.com", "gcsuperuser")
                ud = UserData(username="gcsuperuser", first_name="gcsuperuser", last_name="gcsuperuser", password="gcsuperuser", is_admin=True)
                ud.save()
        except:
            raise CommandError('The superuser could not be created. Did you make sure that your database is created? Seems like the database is not available or we do not have enough permissions to create User and UserData tables.')
        # set the default security questions
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
