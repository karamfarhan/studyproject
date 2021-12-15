from functools import partial
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import serializers, status
from rest_framework.response import Response
from base.models import Message, Room, User, Topic
from .serilizers import DetilRoomSerilizers, UpdateRoomSerilizers, CreateRoomSerilizers, RegisterSerilizers, UserProfileSerilizers, ChangePasswordSerializer, MessagesSerilizers, AllMessagesFromRoomSerilizers
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.generics import UpdateAPIView


@api_view(['GET'])
def getRouts(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)


@api_view(['POST', ])
def registerUser(request):
    if request.method == 'POST':
        data = {}
        email = request.data.get('email', '0')
        if validate_email(email) != None:
            data['error_message'] = 'That email is already in use.'
            data['response'] = 'Error'
            return Response(data)

        username = request.data.get('username', '0')
        if validate_username(username) != None:
            data['error_message'] = 'That username is already in use.'
            data['response'] = 'Error'
            return Response(data)

        serializer = RegisterSerilizers(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'successfully registered new user.'
            data['email'] = user.email
            data['username'] = user.username
            data['pk'] = user.pk
            token = Token.objects.get(user=user).key
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)


def validate_email(email):
    account = None
    try:
        account = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    if account != None:
        return email


def validate_username(username):
    account = None
    try:
        account = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    if account != None:
        return username
###############################


@api_view(['POST', ])
def loginUser(request):
    if request.method == 'POST':
        context = {}
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            context['response'] = "Successfully authenticated."
            context['id'] = user.pk
            context['email'] = user.email
            context['token'] = token.key
        else:
            context['response'] = "Error"
            context['error_message'] = "Invalid credentials"
        return Response(context)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def profileUser(request):
    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = UserProfileSerilizers(user)
        return Response(serializer.data)


@api_view(['PUT', ])
@permission_classes((IsAuthenticated,))
def updateprofileUser(request):
    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "PUT":
        serializer = UserProfileSerilizers(
            user, data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data["response"] = "Successfully updated"
            data['pk'] = user.pk
            data['email'] = user.email
            data['username'] = user.username
            data['name'] = user.name
            data['bio'] = user.bio
            avatar_url = str(request.build_absolute_uri(user.avatar.url))
            if "?" in avatar_url:
                avatar_url = avatar_url[:avatar_url.rfind("?")]
            data['avatar'] = avatar_url
            return Response(data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            # confirm the new passwords match
            new_password = serializer.data.get("new_password")
            confirm_new_password = serializer.data.get("confirm_new_password")
            if new_password != confirm_new_password:
                return Response({"new_password": ["New passwords must match"]}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"response": "successfully changed password"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


class getRooms(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = DetilRoomSerilizers
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('topic__name', 'name', 'description', 'host__username')


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getRoom(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serilizers = DetilRoomSerilizers(room, many=False)
        return Response(serilizers.data)


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def updateRoom(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if room.host != user:
        return Response({'response': "you don't have permission "})

    topic_name = request.POST.get('topic')
    if topic_name == "":
        return Response({"response": "Enter a topic"})
    topic, create = Topic.objects.get_or_create(name=topic_name)
    room.topic = topic
    if request.method == 'PUT':
        serilizers = UpdateRoomSerilizers(
            room, data=request.data, partial=True)
        data = {}
        if serilizers.is_valid():
            serilizers.save()
            data['response'] = "update successful"
            data['pk'] = room.id
            data['host'] = room.host.username
            data['topic'] = room.topic.name
            data['name'] = room.name
            data['description'] = room.description
            data['participants'] = room.participants.values_list(
                'id', flat=True)
            data['date_update'] = room.updated
            return Response(data=data)
        return Response(serilizers.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def deleteRoom(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user
    if room.host != user:
        return Response({'response': "you don't have permission "})
    if request.method == 'DELETE':
        operation = room.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def createRoom(request):
    user = request.user
    topic_name = request.POST.get('topic')
    if topic_name == "":
        return Response({"response": "Enter a topic"})
    topic, create = Topic.objects.get_or_create(name=topic_name)
    room = Room(host=user, topic=topic)
    if request.method == "POST":
        serializers = CreateRoomSerilizers(
            room, data=request.data, partial=True)
        data = {}
        if serializers.is_valid():
            serializers.save()
            data['response'] = "create successful"
            data['pk'] = room.id
            data['host_id'] = room.host.id
            data['host_username'] = room.host.username
            data['topic'] = room.topic.name
            data['name'] = room.name
            data['description'] = room.description
            data['date_created'] = room.created
            return Response(data=data)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def api_is_author_of_room(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {}
    user = request.user
    if room.host != user:
        data['response'] = "You don't have permission to edit that."
        return Response(data=data)
    data['response'] = "You have permission to edit that."
    return Response(data=data)


@api_view(['GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def get_delete_messages(request, pk):
    try:
        message = Message.objects.get(id=pk)
    except Message.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = MessagesSerilizers(message)
        return Response(serializer.data)
    user = request.user
    if message.user != user:
        return Response({'response': "you don't have permission "})

    if request.method == 'DELETE':
        operation = message.delete()
        data = {}
        if operation:
            data["success"] = "delete successful"
        else:
            data["failure"] = "delete failed"
        return Response(data=data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def createmessage(request):
    user = request.user
    room_id = request.POST.get('room')
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "POST":
        message = Message.objects.create(
            user=user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(user)
        serializer = MessagesSerilizers(
            message, data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            data['response'] = "create successfully"
            data['body'] = message.body
            data['room'] = message.room.id
            data['user'] = message.user.id
            data['date_created'] = message.created
            serializer.save()
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_all_messages_from_room(request, pk):
    try:
        room = Room.objects.get(id=pk)
    except Room.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        messages = Message.objects.filter(room=room)
        serializer = AllMessagesFromRoomSerilizers(messages, many=True)
        return Response(serializer.data)
