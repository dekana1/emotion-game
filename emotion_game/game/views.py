from audioop import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth import login
from django.contrib.auth import logout as django_logout
from django.http import JsonResponse
from django.core import serializers
from sklearn.feature_extraction import DictVectorizer
import ml_model
import pandas as pd
import random
import os
import pickle
import re
from collections import Counter

import json

from .models import Player
from django.contrib.auth.models import User
from django.db import IntegrityError

# Create your views here.

data_df = pd.read_csv('words_emotions.csv', index_col='word')
data_df.index = [word.strip() for word in data_df.index]


def ngram(token, n):
    output = []
    for i in range(n-1, len(token)):
        ngram = ' '.join(token[i-n+1:i+1])
        output.append(ngram)
    return output


def create_feature(text, nrange=(1, 1)):
    text_features = []
    text = text.lower()
    text_alphanum = re.sub('[^a-z0-9#]', ' ', text)
    for n in range(nrange[0], nrange[1]+1):
        text_features += ngram(text_alphanum.split(), n)
    text_punc = re.sub('[a-z0-9]', ' ', text)
    text_features += ngram(text_punc.split(), 1)
    return Counter(text_features)


model = pickle.load(open('model.pkl', 'rb+'))
print(model)


# Game's front page 

def front(request):

    return render(request, 'index.html')



def write_json(new_data, filename='user_data.json'):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["players"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)


# Check user name exists


def check_username(request):
    # username = request.GET.get("new-user-name-input")
    # data = {
    #     'username_exists': User.objects.filter(username=username).exists()
    # }
    # print('data', data)
    return JsonResponse()

# user signin 
def signup(request):
    context = {}
    print("signup", request.user)
    if request.method == 'POST':
        
        new_user_name = request.POST.get('new-user-name-input')
        
        try:
            user = User.objects.create(username=new_user_name)
            new_player = Player.objects.create(name=user)
            new_player.save()

        except IntegrityError:
            messages.error(request, "That username already exist")

    context['user_info'] = Player.objects.all()
    
    return render(request, 'signin.html', context)


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.get(username=username)

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        print(request.user)

        return redirect('game:home')

    return render(request, 'signin.html')

# Selects the sentiment of the game stage

def game_choice():

    round_choices = ["Joy", 'Fear', "Anger", "Sadness", "Disgust", "Shame", "Guilt"]

    current_round_sentiment = random.choice(round_choices)

    return current_round_sentiment


# Generates the 15 words advised to be used in creating user sentence

def word_bag_generator():
    permitted_words = [x for x in random.choices(list(data_df.index.values), k=15)]

    return permitted_words


# View function for game home page 
@login_required
def home(request):
    context = dict()
    context['game_choice'] = game_choice()
    context['word_bag'] = word_bag_generator()
    context['user'] = ''
    print("in home", request.user)
    return render(request, 'home.html', context)


# predicts user sentence and awards stars

def predictor(request):
    
    context = dict()

    congrats_words = ['Success', 'Good Job', 'Well done', 'Awesome']
    failure_words = ['Uh-Oh', 'Too Bad', 'Try Again', 'Sorry']

    stars = 0

    if request.method == 'POST':
        # Get user_entry, given word bank, and game stage sentiment 

        user_entry = request.POST.get('user_entry')
        word_bank = request.POST.get('word_bank')
        game = request.POST.get("game_choice")

        # print(game)
        # print(word_bank)

        # Convert entry into features and make predictions 

        features = create_feature(user_entry, nrange=(1, 4))
        features = ml_model.vectorizer.transform(features)
        predicted_emotion = model.predict(features)[0]


        predicted_emotion = str(predicted_emotion).capitalize()

        context['result'] = predicted_emotion
        context['game'] = game
        
        # Awarding of stars 

        # if user_entry matches given game sentiment

        player = Player.objects.get(name=request.user)
        # print('player name', player.name)

        if game == predicted_emotion:
            context['result_header'] = random.choice(congrats_words)

            # counts number or words used from word bank

            word_count = 0

            for x in user_entry.split():
                if x in word_bank:
                    word_count += 1
            
            if word_count <= 2:
                stars = 1

            elif word_count in range(3, 6):
                stars = 2
            
            elif word_count in range(6, 9):
                stars = 3
            
            else: 
                stars = 4

            context['current_stars'] = stars
            
            # update players stars
            player.stars += stars
            player.save()


        # if user_entry doesn't match sentiment
        else:
            context['result_header'] = random.choice(failure_words)
            context['current_stars'] = stars

        context['total_stars'] = player.stars
    return render(request, 'result.html', context)


def logout(request):
    django_logout(request)
    return redirect('game:front')