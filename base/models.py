from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200) # charfiled for small text fields like names, titles, ..etc
    #text fields for larger fields where no max_length required 
    description = models.TextField(null=True, #tells that its ok to store null if user didn't enter thing in this field
                                    blank=True) #tells the field can be empty in forms when user submitting
    #participents = 
    updated = models.DateTimeField(auto_now=True) #get timestamp of last update to the row
    created = models.DateTimeField(auto_now_add=True) #get timestamp of row creation time

    class Meta:
        ordering = ['-updated', '-created'] 


    def __str__(self): # __str__ tells to execute this block automatically if we use print(Room) or str(Room)
        return self.name
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # create a key and tells if the reference Room gets deleted, delete message also
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50] # return only first 50 character
