from django.db import models

# Create your models here.


class Video(models.Model):
    """Model definition for Video."""

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    thumbnail_url = models.URLField()
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for Video."""

        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self):
        return self.title
