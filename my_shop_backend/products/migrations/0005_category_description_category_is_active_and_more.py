from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_brand_alter_product_description_productcolor_and_more'),
    ]

    operations = [
        # Category new fields
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='category',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        # Product new fields
        migrations.AddField(
            model_name='product',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=300, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='product',
            name='short_description',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='product',
            name='compare_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='cost_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='min_stock',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_new',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='is_sale',
            field=models.BooleanField(default=False),
        ),
    ]
