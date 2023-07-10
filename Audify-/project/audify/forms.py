from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Video
from .models import Comments

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'source_type', 'video_file', 'link']

class CommentUploadForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('comments','timestamps')