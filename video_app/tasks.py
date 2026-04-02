import os
import subprocess

import django_rq
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import force_bytes

User = get_user_model()
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

    base_dir = os.path.join(settings.MEDIA_ROOT, "videos", str(video_id))
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


@django_rq.job("fast")
def send_activation_email(user_id):
    user = User.objects.filter(id=user_id).first()

    uidb64 = urlsafe_base64_encode(force_bytes(user_id))
    token = default_token_generator.make_token(user)

    activation_link = f"http://127.0.0.1:5500/pages/auth/activate.html?uid={uidb64}&token={token}"
    html_content = render_to_string(
        "emails/activation.html",
        {"activation_link": activation_link, "user_email": user.email},
    )

    plain_text = f"""
        Hi {user.email}!

        Click here to activate your Videoflix account:
        {activation_link}

        Thanks,
        Videoflix Team
    """

    send_mail(
        subject="Activate your Videoflix account",
        html_message=html_content,
        message=plain_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@django_rq.job("fast")
def send_reset_password_email(user_id):
    user = User.objects.filter(id=user_id).first()

    uidb64 = urlsafe_base64_encode(force_bytes(user_id))
    token = default_token_generator.make_token(user)

    reset_password_link = f"http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
    html_content = render_to_string(
        "emails/reset_password.html",
        {
            "reset_password_link": reset_password_link,
            "user_email": user.email,
        },
    )
    plain_text = f"""
        Hi {user.email}!,

        Click below to reset your password::
        {reset_password_link}

        Videoflix Team
        """
    send_mail(
        subject="Reset password for your Videoflix account",
        html_message=html_content,
        message=plain_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
