from django.contrib import admin

from video_app.models import Video
from video_app.tasks import transcode_video

# Register your models here.


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "status", "created_at"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            transcode_video.delay(obj.id)
