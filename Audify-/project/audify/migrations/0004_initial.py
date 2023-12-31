# Generated by Django 4.1.6 on 2023-06-24 12:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('audify', '0003_delete_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('source_type', models.CharField(choices=[('file', 'File'), ('youtube', 'YouTube')], max_length=10)),
                ('video_file', models.FileField(blank=True, upload_to='media/')),
                ('youtube_link', models.URLField(blank=True)),
                ('audio_file', models.FileField(blank=True, upload_to='media/')),
                ('subtitles_file', models.FileField(blank=True, upload_to='media/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
