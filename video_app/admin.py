from django.contrib import admin

from video_app.models import Video

# Register your models here.


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "created_at"]
