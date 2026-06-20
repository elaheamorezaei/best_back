from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banners', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='button_text',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='banner',
            name='mobile_image',
            field=models.ImageField(blank=True, null=True, upload_to='banners/mobile/'),
        ),
        migrations.AddField(
            model_name='banner',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='banner',
            name='subtitle',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='banner',
            name='title',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
