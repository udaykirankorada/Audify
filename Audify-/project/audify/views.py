import os
import uuid
from pytube import YouTube
from pydub import AudioSegment
from mutagen.mp3 import MP3

import requests
import subprocess
import os
import uuid
import datetime
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.files import File
from .forms import *
from moviepy.editor import VideoFileClip
from datetime import timedelta
from django.core.files.temp import NamedTemporaryFile
from .models import *
# Create your views here.
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse


def convert_to_audio(video_path, output_path):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(output_path, codec='pcm_s16le')
    video_clip.close()
    audio_clip.close()

def mutagen_length(path):
    try:
        audio = MP3(path)
        length = audio.info.length
        return length
    except:
        return None

def format_duration(duration_seconds):
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def extract_audio_from_facebook(url):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'audios/')
    os.makedirs(output_dir, exist_ok=True)
    fileid=str(uuid.uuid4())
    command = ['youtube-dl', '--extract-audio', '--audio-format', 'mp3', '--output', f'{output_dir}/{fileid}.%(ext)s', url]
    try:
        subprocess.run(command, check=True)
        return True , f'{output_dir}/{fileid}.mp3'
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract audio: {e}")
        return False , None
    
def extract_audio_from_twitch(url):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'audios/')
    os.makedirs(output_dir, exist_ok=True)
    fileid=str(uuid.uuid4())
    command = f'youtube-dl --extract-audio --audio-format mp3 --output {output_dir}/{fileid}.%(ext)s {url}'
    try:
        subprocess.run(command, check=True)
        return True , f'{output_dir}/{fileid}.mp3'
    except subprocess.CalledProcessError as e:
        print(f"Failed to extract audio: {e}")
        return False , None

@login_required(login_url='loginPage')
def dashboard(request):
    videos = Video.objects.filter(user=request.user)  # Filter videos based on the customer
    no_of_videos=videos.count()
    context = {'videos':videos,'no':no_of_videos}
    return render(request, 'audify/dashboard.html',context)

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request,'Account is successfully created for ' + user)
            return redirect ('loginPage')

    context ={'form':form}
    return render(request,'audify/register.html',context)

@unauthenticated_user
def login_process(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'username or password is incorrect')

    return render(request,'audify/login.html')

def logoutuser(request):
    logout(request)
    return redirect('loginPage')


@login_required(login_url='loginPage')
def home(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            if video.source_type == 'youtube' :
                youtube_link = form.cleaned_data['link']
                title = form.cleaned_data['title']
                yt = YouTube(youtube_link)
                video_path = yt.streams.first().download()
                clip = VideoFileClip(video_path)
                duration_seconds = int(clip.duration)
                clip.close()
                duration_formatted = format_duration(duration_seconds)
                video.duration = duration_formatted

                
                # Extract audio only
                audio = yt.streams.filter(only_audio=True).first()

                # Replace 'destination' with the path where you want to save the download file
                destination = os.path.join(settings.MEDIA_ROOT, 'audios/')

                # Generate a UUID-based filename
                audio_filename = str(uuid.uuid4()) + '.mp3'

                # Download the file
                out_file = audio.download(output_path=destination)

                # Save the file with the generated filename
                new_file = os.path.join(destination, audio_filename)
                os.rename(out_file, new_file)                
                video.audio_file.save(audio_filename, open(new_file, 'rb'))
                video.title = title                
                video.save()
                os.remove(video_path)
                os.remove(new_file)
                # Result of success
                video_id=video.id
                return redirect('audio_page', audio_id=str(video_id))
            elif video.source_type == 'facebook' :
                facebook_link = form.cleaned_data['link']
                title = form.cleaned_data['title']
                success , audiofilepath = extract_audio_from_facebook(facebook_link)
                if success:
                    video.audio_file.save(audiofilepath.split('/')[-1],open(audiofilepath, 'rb'))
                    video.title=title
                    video_id=video.id
                    project_folder = os.getcwd()
                    audio_file_path = os.path.join(project_folder, 'media', 'audios', f'{audiofilepath.split("/")[-1]}')
                    #audio = AudioSegment.from_file(audio_file_path)
                    duration = mutagen_length(audio_file_path)
                    duration_formatted = format_duration(int(duration))
                    video.duration = duration_formatted
                    video.save()
                    os.remove(audiofilepath)
                    return redirect('audio_page', audio_id=str(video_id))
                else:
                    form = VideoUploadForm()
                    return render(request, 'audify/home.html', {'form': form})
            elif video.source_type == 'twitch' :
                twitch_link = form.cleaned_data['link']
                title = form.cleaned_data['title']
                success , audiofilepath = extract_audio_from_twitch(twitch_link)
                if success:
                    video.audio_file.save(audiofilepath.split('/')[-1],open(audiofilepath, 'rb'))
                    video.title=title
                    video_id=video.id
                    project_folder = os.getcwd()
                    audio_file_path = os.path.join(project_folder, 'media', 'audios', f'{audiofilepath.split("/")[-1]}')
                    #audio = AudioSegment.from_file(audio_file_path)
                    duration = mutagen_length(audio_file_path)
                    duration_formatted = format_duration(int(duration))
                    video.duration = duration_formatted
                    video.save()
                    os.remove(audiofilepath)
                    return redirect('audio_page', audio_id=str(video_id))
                else:
                    form = VideoUploadForm()
                    return render(request, 'audify/home.html', {'form': form})
                                           
            elif video.source_type == 'file' :

                # Assign the current user's customer model
                video.save()
                video_path = video.video_file.path
                
                

                # Get the duration of the video
                clip = VideoFileClip(video_path)
                duration_seconds = int(clip.duration)
                clip.close()

                # Convert duration to hh:mm:ss format
                duration_formatted = format_duration(duration_seconds)

                # Save the duration in the model
                video.duration = duration_formatted
                video.save()

                # Generate unique name for audio file
                audio_filename = f"{uuid.uuid4()}.wav"

                # Specify the output directory for audio files
                audio_output_dir = os.path.join(settings.MEDIA_ROOT, 'audios/')

                # Create the output directory if it doesn't exist
                os.makedirs(audio_output_dir, exist_ok=True)

                # Specify the output path for the audio file
                audio_output_path = os.path.join(audio_output_dir, audio_filename)
                print(audio_output_path)
                # Convert video to audio
                convert_to_audio(video_path, audio_output_path)

                # Save the audio file path in the model
                video.audio_file.name = os.path.join('audios', audio_filename)
                video.save()
                video_id=video.id
                return redirect('audio_page', audio_id=str(video_id))
    else:
        form = VideoUploadForm()
        return render(request, 'audify/home.html', {'form': form})

@login_required(login_url='loginPage')
def delete_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    video.delete()
    return redirect('video_list')

@login_required(login_url='loginPage')
def delete_comment(request, comment_id,video_id):
    comment = get_object_or_404(Comments, pk=comment_id)
    comment.delete()
    return redirect('audio_page', audio_id=str(video_id))

def save_comments(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')  # Assuming you have a unique identifier for the video
        comments = request.POST.get('comments')
        timestamp = request.POST.get('timestamp')

        # Retrieve the video object based on the video_id
        video = Video.objects.get(id=video_id)

        # Append the new comments and timestamp to the existing ones
        video.comments += '\n' + comments
        video.timestamps += '\n' + timestamp

        # Save the updated video object
        video.save()

        return JsonResponse({'message': 'Comments saved successfully.'})

    return JsonResponse({'error': 'Invalid request method.'})

@login_required(login_url='login')
def audio_page(request, audio_id):
    video = get_object_or_404(Video, pk=audio_id)

    if request.method == "POST":
        form = CommentUploadForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user  # Assign the current user's customer model  
            comment.video = video  # Associate the comment with the video
            comment.save()
            return redirect(request.path)
    else:
        form = CommentUploadForm()

    comments = Comments.objects.filter(video=video)  # Retrieve comments for the video
    context = {'video': video, 'form': form, 'comments': comments}
    return render(request, 'audify/audio_page.html', context)