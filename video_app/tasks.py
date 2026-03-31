import os
import subprocess

import django_rq
from django.conf import settings

QUALITY_PROFILES = [
    {
        "resolution": "360p",
        "scale": "640:360",
        "bitrate": "800k",
        "audio": "96k",
    },
    {
        "resolution": "480p",
        "scale": "854:480",
        "bitrate": "1400k",
        "audio": "128k",
    },
    {
        "resolution": "720p",
        "scale": "1280:720",
        "bitrate": "2800k",
        "audio": "128k",
    },
    {
        "resolution": "1080p",
        "scale": "1920:1080",
        "bitrate": "5000k",
        "audio": "192k",
    },
]


@django_rq.job("default")
def transcode_video(video_id):
    """Background task to transcode uploaded videos into HLS format using FFmpeg."""
    from video_app.models import Video

    video = Video.objects.get(id=video_id)
    video.status = "processing"
    video.save(update_fields=["status"])

    base_dir = os.path.join(settings.MEDIA_ROOT, "video", str(video_id))
    os.makedirs(base_dir, exist_ok=True)

    try:
        variant_playlists = []

        for profile in QUALITY_PROFILES:
            quality_dir = os.path.join(base_dir, profile["resolution"])
            os.makedirs(quality_dir, exist_ok=True)

            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    video.video_file.path,
                    "-vf",
                    f"scale={profile['scale']}",
                    "-vcodec",
                    "libx264",
                    "-crf",
                    "23",
                    "-b:v",
                    profile["bitrate"],
                    "-acodec",
                    "aac",
                    "-b:a",
                    profile["audio"],
                    "-hls_time",
                    "5",
                    "-hls_playlist_type",
                    "vod",
                    "-hls_segment_filename",
                    f"{quality_dir}/segment_%03d.ts",
                    f"{quality_dir}/index.m3u8",
                ],
                check=True,
            )

            variant_playlists.append(profile)

        master_path = os.path.join(base_dir, "master.m3u8")
        with open(master_path, "w", encoding="utf-8") as f:
            f.write(
                "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-INDEPENDENT-SEGMENTS\n\n"
            )

            for profile in QUALITY_PROFILES:
                bandwidth = int(profile["bitrate"].replace("k", "")) * 1000
                resolution = profile["scale"].replace(":", "x")
                f.write(
                    f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution}\n"
                )
                f.write(f'{profile["resolution"]}/index.m3u8\n')

        video.status = "done"
        video.save(update_fields=["status"])

    except subprocess.CalledProcessError:
        video.status = "failed"
        video.save(update_fields=["status"])
