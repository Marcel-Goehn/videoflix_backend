from django.db import models

# Create your models here.


class Video(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    thumbnail_url = models.URLField()
    category = models.CharField(max_length=100)
    video_file = models.FileField(blank=True)

    def __str__(self):
        return self.title
