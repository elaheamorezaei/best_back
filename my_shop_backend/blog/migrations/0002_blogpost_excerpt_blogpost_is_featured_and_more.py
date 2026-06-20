from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='excerpt',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='published_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
