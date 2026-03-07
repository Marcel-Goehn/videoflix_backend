import os
import subprocess

from django.conf import settings

from video_app.models import Video


def convert_video(source, quality):
    """
    Converts the uploaded video to the desired quality
    with the help of ffmpeg
    """
    base = os.path.splitext(source)[0]
    new_file_name = f'{base}_{quality}p.mp4'
    cmd = 'ffmpeg -i "{}" -vf scale=-2:{} -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, quality, new_file_name)
    subprocess.run(cmd, shell=True, capture_output=True)


def delete_converted_videos(source, quality):
    """
    Deletes all video files, after the user deletes it via
    the admin dashboard
    """
    base = os.path.splitext(source)[0]
    file_path = f'{base}_{quality}p.mp4'
    if os.path.exists(file_path):
        os.remove(file_path)


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