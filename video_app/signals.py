import os

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from video_app.models import Video


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):

    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
