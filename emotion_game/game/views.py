from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core import serializers
from sklearn.feature_extraction import DictVectorizer
import ml_model
import pandas as pd
import random
import os
import pickle

# feature_creation = open('ml_model.py')

# Create your views here.


data_df = pd.read_csv('words_emotions.csv', index_col='word')
data_df.index = [word.strip() for word in data_df.index]

model = pickle.load(open('model.pkl', 'rb+'))
print(model)


def game_choice():

    round_choices = ["Joy", 'Fear', "Anger", "Sadness", "Disgust", "Shame", "Guilt"]

    current_round_sentiment = random.choice(round_choices)

    return current_round_sentiment


def word_bag_generator():
    permitted_words = [x for x in random.choices(list(data_df.index.values), k=15)]

    return permitted_words


def front(request):

    return render(request, 'index.html')


def home(request):
    context = dict()
    context['game_choice'] = game_choice()
    context['word_bag'] = word_bag_generator()

    return render(request, 'home.html', context)


def predictor(request):
    #initializations

    context = dict()

    congrats_words = ['Success', 'Good Job', 'Weldone', 'Awesome']
    failure_words = ['Uh-Oh', 'Too Bad', 'Nice try', 'Sorry']
    stars = 0

    if request.method == 'POST':
    

        user_entry = request.POST.get('user_entry')
        word_bank = request.POST.get('word_bank')
        game = request.POST.get("game_choice")

        print(game)
        print(word_bank)

        features = ml_model.create_feature(user_entry, nrange=(1, 4))
        features = ml_model.vectorizer.transform(features)
        predicted_emotion = model.predict(features)[0]


        predicted_emotion = str(predicted_emotion).capitalize()

        context['result'] = predicted_emotion
        context['game'] = game
        
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

            context['stars'] = stars
            
        else:
            context['result_header'] = random.choice(failure_words)
            context['stars'] = stars

    return render(request, 'result.html', context)

