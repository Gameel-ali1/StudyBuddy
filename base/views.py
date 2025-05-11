from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest


# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exist')

    context = {'page': page, }
    return render(request, "base/login_register.html", context)


def registerPage(request):
    form = UserCreationForm()  # get the creation form
    if request.method == "POST":  # check if submit
        form = UserCreationForm(request.POST)  #send this data to the form
        if form.is_valid:  # if the data is valid
            user = form.save(
                commit=False)  #we will save but need to keep use here to do some modification instead of sending then calling it again
            user.username = user.username.lower()  #make sure username is lowercase
            user.save()  # save the modified version of the form
            login(request, user)  #login the user
            return redirect('home')  #redirect to home
        else:
            messages.error(request, 'An error occured during registration')

    context = {'form': form, }
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    query = request.GET.get('q') if request.GET.get(
        'q') != None else ''  #make sure it is empty string if the returned value is None and it returns None only in All link
    rooms = Room.objects.filter(
        Q(topic__name__contains=query) |
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains =query)
    )
    rooms_count = rooms.count()
    topics = Topic.objects.all()
    context = {'rooms': rooms, 'topics': topics, 'rooms_count': rooms_count, 'room_messages': room_messages}  #context
    return render(request, 'base/home.html', context)


def room(request: HttpRequest, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == "POST":
        if request.user.is_authenticated:
            room_messages.create(
                user=request.user,
                room=room,
                body=request.POST.get('body')
            )
            room.participants.add(request.user)
            return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context ={'user': user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):  # form to view the room_form.html
    form = RoomForm()  # first we will set form variable to the form the model-based form
    if request.method == 'POST':  # make sure that we are using POST
        form = RoomForm(request.POST)  # POST the input from the user back to the model-based form to handle it
        if form.is_valid():  # check if all data inside the form is valid
            form.save()  # save the form
            return redirect('home')  # we can use 'home' here because we specified this as a name inside urlpatterns
    context = {'form': form}  # our normal context
    return render(request, 'base/room_form.html', context)  # and the render


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)  #set the room to the data using the ID
    form = RoomForm(instance=room)  #fill the form with the data you got, so the user see what is the old form

    if request.user != room.host:
        return HttpResponse("you aren't allowed to delete others' rooms")
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)  # to fill the old row with the new data
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("you aren't allowed to delete others' rooms")
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("you aren't allowed to delete others' rooms")
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})
