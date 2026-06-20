from django.db import models
from products.models import Category


class CompareDescription(models.Model):
    """Per-category descriptive text shown at the bottom of the compare page."""
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name='compare_description',
    )
    title = models.CharField(max_length=300)
    content = models.TextField(help_text='Paragraphs separated by \\n\\n')

    def __str__(self):
        return f"Compare description: {self.category.name}"
