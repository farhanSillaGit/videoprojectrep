from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(default=0)
    video_file = models.FileField(upload_to='videos/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
