from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create an admin (staff) user'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Admin email')
        parser.add_argument('--password', type=str, required=True, help='Admin password')
        parser.add_argument('--name', type=str, default='ادمین', help='Full name')
        parser.add_argument('--role', type=str, default='superadmin',
                            choices=['superadmin', 'admin', 'editor', 'support'],
                            help='Admin role')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']
        role = options['role']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'کاربر با ایمیل {email} قبلاً وجود دارد.'))
            user = User.objects.get(email=email)
            user.is_staff = True
            user.is_superuser = (role == 'superadmin')
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS('رمز عبور و دسترسی آپدیت شد.'))
        else:
            username = email.split('@')[0]
            base = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'{base}{counter}'
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_superuser=(role == 'superadmin'),
            )
            self.stdout.write(self.style.SUCCESS(f'کاربر {email} ساخته شد.'))

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.full_name = name
        profile.role = role
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ ادمین آماده است:\n'
            f'   Email   : {email}\n'
            f'   Password: {password}\n'
            f'   Role    : {role}\n'
            f'   is_staff: True\n'
        ))
