import os
import shutil
import subprocess

from django.conf import settings

from video_app.models import Video


def convert_video(source, quality, video_pk):
    """
    Converts the uploaded video to HLS format at the desired quality.
    """
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_pk), f'{quality}p')
    os.makedirs(output_dir, exist_ok=True)
    manifest = os.path.join(output_dir, 'index.m3u8')
    cmd = (
        'ffmpeg -i "{}" -vf scale=-2:{} -c:v libx264 -crf 23 -c:a aac -strict -2 '
        '-start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{}"'
    ).format(source, quality, manifest)
    subprocess.run(cmd, shell=True, capture_output=True)


def delete_hls_video(video_pk):
    """
    Deletes the HLS directory for a video after it is removed via the admin dashboard.
    """
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_pk))
    if os.path.exists(hls_dir):
        shutil.rmtree(hls_dir)


def generate_thumbnail(source, instance_pk):
    """
    Extracts a single frame at 1 second as a JPEG thumbnail,
    then saves the full URL to the Video instance's thumbnail_url field.
    """
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnail')
    os.makedirs(thumbnails_dir, exist_ok=True)
    filename = os.path.splitext(os.path.basename(source))[0] + '_thumbnail.jpg'
    thumbnail_path = os.path.join(thumbnails_dir, filename)
    cmd = 'ffmpeg -i "{}" -ss 00:00:01.000 -vframes 1 "{}"'.format(source, thumbnail_path)
    subprocess.run(cmd, shell=True, capture_output=True)
    if os.path.exists(thumbnail_path):
        relative_path = os.path.relpath(thumbnail_path, settings.MEDIA_ROOT).replace('\\', '/')
        url = f"http://localhost:8000{settings.MEDIA_URL}{relative_path}"
        Video.objects.filter(pk=instance_pk).update(thumbnail_url=url)