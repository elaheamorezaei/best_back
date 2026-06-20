from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='cons',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='comment',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comment',
            name='pros',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='comment',
            name='title',
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
