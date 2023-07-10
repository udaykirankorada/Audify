from django.db import models
from pytz import timezone
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.
    
class Video(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    source_type = models.CharField(max_length=10, choices=[('file', 'File'), ('youtube', 'Youtube Link'), ('facebook', 'Facebook Link'), ('twitch', 'Twitch Link')])
    video_file = models.FileField(upload_to='videos/', blank=True)
    link = models.URLField(blank=True)
    duration = models.CharField(max_length=8, blank=True, default='00:00:00')
    audio_file = models.FileField(upload_to='audios/', blank=True)
    subtitles_file = models.FileField(upload_to='subtitles/', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True ,)
    def __str__(self):
        return self.title
    
class Comments(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    comments = models.CharField(max_length=200)
    timestamps = models.CharField(max_length=200)
    def __str__(self):
        return self.comments