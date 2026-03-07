import os

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

import django_rq

from video_app.models import Video
from .utils import convert_video, delete_converted_videos, generate_thumbnail


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    After the original video is uploaded,
    the creation of the additional videos for the right solutions
    is getting added to the queue, so that the user doesn't need
    to wait for it to finish
    """
    if created:
        queue = django_rq.get_queue("default", autocommit=True)
        queue.enqueue(convert_video, instance.video_file.path, 360)
        queue.enqueue(convert_video, instance.video_file.path, 480)
        queue.enqueue(convert_video, instance.video_file.path, 720)
        queue.enqueue(convert_video, instance.video_file.path, 1080)
        queue.enqueue(generate_thumbnail, instance.video_file.path, instance.pk)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Calls the delete functions, to remove the video files
    """
    delete_converted_videos(instance.video_file.path, 360)
    delete_converted_videos(instance.video_file.path, 480)
    delete_converted_videos(instance.video_file.path, 720)
    delete_converted_videos(instance.video_file.path, 1080)
    thumbnail_path = os.path.join(
        settings.MEDIA_ROOT, 'thumbnail',
        os.path.splitext(os.path.basename(instance.video_file.path))[0] + '_thumbnail.jpg'
    )
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)
    if os.path.exists(instance.video_file.path):
        os.remove(instance.video_file.path)
