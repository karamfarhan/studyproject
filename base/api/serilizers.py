from rest_framework import serializers
from base.models import Message, Room, User, Topic
from rest_framework.serializers import ModelSerializer
from PIL import Image


class RegisterSerilizers(serializers.ModelSerializer):

    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user = User(
            username=self.validated_data['username'],
            email=self.validated_data['email'].lower()
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError(
                {'password': 'password must be mutch'})

        user.set_password(password)
        user.save()
        return user


class UserProfileSerilizers(ModelSerializer):
    # avatar = serializers.SerializerMethodField('validate_avatar_url')

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'name', 'bio', 'avatar']

    # def validate_avatar_url(self, user):
    #     avatar = user.avatar.url[:user.avatar.url.rfind("?")]
    #     return avatar


class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)


class DetilRoomSerilizers(ModelSerializer):
    host_username = serializers.SerializerMethodField(
        'get_username_from_host')
    participants = serializers.SerializerMethodField(
        'get_participants_from_room')

    class Meta:
        model = Room
        fields = ["id", "host", "host_username", "topic", "name",
                  "description", "updated", "created", "participants"]

    def get_username_from_host(self, room):
        host_username = room.host.username
        return host_username

    def get_participants_from_room(self, room):
        participants = room.participants.values_list('id', flat=True)
        return participants


class UpdateRoomSerilizers(ModelSerializer):
    class Meta:
        model = Room
        fields = ["topic", "name", "description"]

    def validate(self, room):
        try:
            name = room['name']
            if len(name) < 10:
                raise serializers.ValidationError(
                    {"response": "Enter name Longer than 10"})
        except KeyError:
            pass
        return room


class CreateRoomSerilizers(ModelSerializer):
    class Meta:
        model = Room
        fields = ["topic", "name", "description", "host", "created"]


class MessagesSerilizers(ModelSerializer):
    class Meta:
        model = Message
        fields = ["body", "room", "user", "created"]


class AllMessagesFromRoomSerilizers(ModelSerializer):
    username = serializers.SerializerMethodField(
        'get_username_from_message')

    class Meta:
        model = Message
        fields = ["id", "body", "username"]

    def get_username_from_message(self, message):
        return message.user.username
