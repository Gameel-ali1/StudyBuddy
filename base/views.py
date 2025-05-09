from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic
from .forms import RoomForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.
def loginPage(request):
        if request.user.is_authenticated:
                return redirect('home')

        if request.method=='POST':
                username = request.POST.get('username')
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

        context = {}
        return render(request, "base/login_register.html", context)


def logoutUser(request):
        logout(request)
        return redirect('home')

def home(request):
        query = request.GET.get('q') if request.GET.get('q') != None else '' #make sure it is empty string if the returned value is None and it returns None only in All link
        rooms = Room.objects.filter(
                Q(topic__name__contains=query) |
                Q(name__icontains=query) |
                Q(description__icontains=query)
                )
        rooms_count = rooms.count()
        topics = Topic.objects.all()
        context = {'rooms': rooms, 'topics': topics, 'rooms_count':rooms_count} #context 
        return render(request, 'base/home.html', context)

def room(request, pk):
        room = Room.objects.get(id=pk)
        context = {'room': room}
        return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request): # form to view the room_form.html
        form = RoomForm() # first we will set form variable to the form the model-based form
        if request.method == 'POST': # make sure that we are using POST
                form = RoomForm(request.POST) # POST the input from the user back to the model-based form to handle it
                if form.is_valid(): # check if all data inside the form is valid
                        form.save() # save the form 
                        return redirect('home') # we can use 'home' here because we specified this as a name inside urlpatterns
        context = {'form':form} # our normal context 
        return render(request, 'base/room_form.html', context) # and the render 

@login_required(login_url='login')
def updateRoom(request, pk):
        room = Room.objects.get(id=pk) #set the room to the data using the ID
        form = RoomForm(instance=room) #fill the form with the data you got, so the user see what is the old form
        
        if request.user != room.host:
                return HttpResponse("you aren't allowed to delete others' rooms")
        if request.method == "POST":
                form = RoomForm(request.POST, instance=room) # to fill the old row with the new data
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
