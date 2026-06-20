from django.db import models


class AboutSlider(models.Model):
    image = models.ImageField(upload_to='about/slider/')
    alt = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Slider'

    def __str__(self):
        return self.alt


class AboutStoryParagraph(models.Model):
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text[:60]


class AboutWhyUsItem(models.Model):
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class AboutBranchSection(models.Model):
    """Singleton — تصویر بخش شعب"""
    image = models.ImageField(upload_to='about/branches/')
    alt = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Branch Section Image'

    def __str__(self):
        return self.alt


class AboutBranch(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=50)
    working_hours = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class AboutDescriptionSection(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class AboutTeamMember(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    avatar = models.ImageField(upload_to='about/team/')
    bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class AboutStat(models.Model):
    label = models.CharField(max_length=200)
    value = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.value}"
