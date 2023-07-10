from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard,name="video_list"),
    path('login/',views.login_process, name="loginPage"),
    path('signup/',views.registerPage, name="registerPage"),
    path('logout/', views.logoutuser, name="logout"),
    path('',views.home,name="home"),
    path('audio/<str:audio_id>/', views.audio_page, name='audio_page'),
    path('delete/<int:video_id>/', views.delete_video, name='delete_video'),
    path('deletecomment/<int:comment_id>/<int:video_id>/', views.delete_comment, name='delete_comment')
]
