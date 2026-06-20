from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slider', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='slider',
            name='mobile_image',
            field=models.ImageField(blank=True, null=True, upload_to='sliders/mobile/'),
        ),
    ]
