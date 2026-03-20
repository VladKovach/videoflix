import django_rq


@django_rq.job("default")
def transcode_video(video_id):
    print(f"Transcoding video {video_id}...")
    # FFmpeg will go here later
