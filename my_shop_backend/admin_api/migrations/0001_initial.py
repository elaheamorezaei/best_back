from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='فروشگاه آنلاین', max_length=200)),
                ('site_description', models.TextField(blank=True)),
                ('site_keywords', models.JSONField(blank=True, default=list)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('favicon', models.ImageField(blank=True, null=True, upload_to='settings/')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('address', models.TextField(blank=True)),
                ('instagram', models.CharField(blank=True, max_length=200)),
                ('telegram', models.CharField(blank=True, max_length=200)),
                ('whatsapp', models.CharField(blank=True, max_length=50)),
                ('google_analytics_id', models.CharField(blank=True, max_length=50)),
                ('google_tag_manager_id', models.CharField(blank=True, max_length=50)),
                ('robots_txt', models.TextField(blank=True, default='User-agent: *\nAllow: /')),
                ('maintenance_mode', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Site Settings',
            },
        ),
        migrations.CreateModel(
            name='ThemeSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary', models.CharField(default='#ef4444', max_length=20)),
                ('secondary', models.CharField(default='#f59e0b', max_length=20)),
                ('accent', models.CharField(default='#8b5cf6', max_length=20)),
                ('neutral', models.CharField(default='#6b7280', max_length=20)),
                ('base', models.CharField(default='#ffffff', max_length=20)),
                ('info', models.CharField(default='#3b82f6', max_length=20)),
                ('success', models.CharField(default='#22c55e', max_length=20)),
                ('warning', models.CharField(default='#f59e0b', max_length=20)),
                ('error', models.CharField(default='#ef4444', max_length=20)),
                ('radius', models.CharField(default='0.75rem', max_length=20)),
                ('font_family', models.CharField(default='Vazir', max_length=100)),
                ('mode', models.CharField(default='light', max_length=10)),
            ],
            options={
                'verbose_name': 'Theme Settings',
            },
        ),
        migrations.CreateModel(
            name='SEOPageSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.CharField(max_length=100)),
                ('path', models.CharField(max_length=200, unique=True)),
                ('meta_title', models.CharField(blank=True, max_length=300)),
                ('meta_description', models.TextField(blank=True)),
                ('keywords', models.JSONField(blank=True, default=list)),
                ('og_image', models.CharField(blank=True, max_length=500)),
                ('no_index', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'SEO Page Settings',
            },
        ),
        migrations.CreateModel(
            name='OrderNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('is_admin', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notes',
                    to='orders.order',
                )),
                ('author', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
