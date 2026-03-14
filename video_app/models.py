from django.db import models


class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    thumbnail_url = models.URLField()
    category = models.CharField(max_length=100)
    video_file = models.FileField()

    def __str__(self):
        return self.title
