from rest_framework.generics import ListAPIView

from video_app.api.serializers import VideoSerializer
from video_app.models import Video


class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoPlaylistView:
    pass


class VideoSegmentView:
    pass
