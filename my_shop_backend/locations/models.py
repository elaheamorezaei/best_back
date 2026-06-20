from django.db import models


class Province(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class City(models.Model):
    province = models.ForeignKey(Province, related_name='cities', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.province.name} — {self.name}"
