from django.db import models


class SocialLink(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    label = models.CharField(max_length=100)
    href = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class CustomerServiceLink(models.Model):
    text = models.CharField(max_length=200)
    href = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class ProductLink(models.Model):
    text = models.CharField(max_length=200)
    href = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class AboutUsLink(models.Model):
    text = models.CharField(max_length=200)
    href = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class FeatureBox(models.Model):
    icon = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class PartnerLogo(models.Model):
    src = models.ImageField(upload_to='partners/')
    alt = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.alt
