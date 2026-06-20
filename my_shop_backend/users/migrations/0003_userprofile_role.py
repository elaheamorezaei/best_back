from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userprofile_address_userprofile_birth_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                blank=True,
                choices=[
                    ('superadmin', 'Super Admin'),
                    ('admin', 'Admin'),
                    ('editor', 'Editor'),
                    ('support', 'Support'),
                ],
                max_length=20,
            ),
        ),
    ]
