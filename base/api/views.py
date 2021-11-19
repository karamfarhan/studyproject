from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.api import serilizers
from base.models import Room
from .serilizers import RoomSerilizers


@api_view(['GET'])
def getRouts(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)


@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serilizers = RoomSerilizers(rooms, many=True)
    return Response(serilizers.data)


@api_view(['GET'])
def getRoom(request, pk):
    room = Room.objects.get(id=pk)
    serilizers = RoomSerilizers(room, many=False)
    return Response(serilizers.data)
