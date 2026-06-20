from django.db import models


class TrendingSearch(models.Model):
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    @property
    def link(self):
        return f"/search?q={self.title}"

    def __str__(self):
        return self.title
