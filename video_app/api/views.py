import os

from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponse
from django.views import View
from rest_framework.generics import ListAPIView

from core import settings
from video_app.api.serializers import VideoSerializer
from video_app.models import Video

User = get_user_model()


class VideoListView(ListAPIView):
    """API view to list all videos"""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoPlaylistView(View):
    """View to serve HLS playlist files for videos"""

    def get(self, request, movie_id, resolution):
        """Serve the HLS playlist file for the specified movie and resolution."""
        playlist_path = ""
        try:
            playlist_path = f"{settings.MEDIA_ROOT}/video/{movie_id}/{resolution}/index.m3u8"
        except:
            raise Http404("Playlist not found")
        with open(playlist_path, "r", encoding="utf-8") as f:
            m3u8_content = f.read()
            response = HttpResponse(
                m3u8_content, content_type="application/vnd.apple.mpegurl"
            )

        return response


class VideoSegmentView(View):
    """View to serve HLS video segment files"""

    def get(self, request, movie_id, resolution, segment):
        """Serve the specified HLS video segment file."""
        segment_path = os.path.join(
            settings.MEDIA_ROOT, "video", str(movie_id), resolution, segment
        )
        if not os.path.exists(segment_path):
            raise Http404("Segment not found")
        with open(segment_path, "rb") as f:
            segment_content = f.read()
            response = HttpResponse(segment_content, content_type="video/mp2t")

        return response
