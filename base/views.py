from django.shortcuts import render, redirect
from . models import Room, Topic
from .forms import RoomForm
from django.db.models import Q
# Create your views here.


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count()
    contxt = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
    }
    return render(request, "base/home.html", contxt)


def room(request, pk):
    room = Room.objects.get(id=pk)
    contxt = {
        "room": room
    }
    return render(request, "base/room.html", contxt)


def createroom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    contxt = {
        "form": form
    }
    return render(request, 'base/room_form.html', contxt)


def updateroom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    contxt = {
        "form": form
    }
    return render(request, 'base/room_form.html', contxt)


def deleteroom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    contxt = {
        "obj": room
    }
    return render(request, 'base/delete.html', contxt)
