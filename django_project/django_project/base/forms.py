from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm

class UserCreationFormClone(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        exclude= ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'avatar', 'email', 'bio', 'username']