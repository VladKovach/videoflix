import os
import shutil

from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from video_app.models import Video


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Delete original video file, thumbnail and generated HLS folder when Video is deleted."""

    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)

    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)

    hls_folder = os.path.join(settings.MEDIA_ROOT, "videos", str(instance.id))
    if os.path.isdir(hls_folder):
        shutil.rmtree(hls_folder)
