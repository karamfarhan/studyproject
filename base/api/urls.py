from django.urls import path

from . import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('', views.getRouts),
    path('register', views.registerUser, name="apiregister"),
    path('login', views.loginUser, name="apilogin"),
    path('userprofile', views.profileUser, name="userprofiledetail"),
    path('userprofile/update', views.updateprofileUser, name="userprofileupdate"),
    path('change_password', views.ChangePasswordView.as_view(),
         name="change_password"),
    path('rooms', views.getRooms.as_view(), name="apirooms"),
    path('rooms/<str:pk>/', views.getRoom, name="apiroom"),
    path('rooms/get_messages/<str:pk>/',
         views.get_all_messages_from_room, name="apiroom"),
    path('rooms/update/<str:pk>/', views.updateRoom, name="apiupdateroom"),
    path('rooms/delete/<str:pk>/', views.deleteRoom, name="apideleteroom"),
    path('rooms/create', views.createRoom, name="apicreateroom"),
    path('rooms/is_author/<str:pk>/',
         views.api_is_author_of_room, name="is_author"),
    path('messages/<str:pk>/', views.get_delete_messages, name='getmessage'),
    path('messages/create', views.createmessage, name='createmessage'),
    path('messages/delete/<str:pk>/',
         views.get_delete_messages, name='deletemessage')
]
