from django.shortcuts import render, redirect
from . models import Room
from .forms import RoomForm
# Create your views here.


def home(request):
    rooms = Room.objects.all()
    contxt = {
        "rooms": rooms
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
