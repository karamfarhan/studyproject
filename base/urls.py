from os import name
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('create_room/', views.createroom, name="create_room"),
    path('update_room/<str:pk>/', views.updateroom, name="update_room"),
    path('delete_room/<str:pk>/', views.deleteroom, name="delete_room")
]
