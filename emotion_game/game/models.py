from pyexpat import model
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Player(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)


    def __str__(self):
        return self.name