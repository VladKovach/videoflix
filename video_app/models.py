from django.db import models

# Create your models here.


class Video(models.Model):
    """Model definition for Video."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    thumbnail = models.FileField(upload_to="thumbnails/", blank=True)
    category = models.CharField(max_length=50)
    video_file = models.FileField(upload_to="videos")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta definition for Video."""

        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self):
        return self.title
