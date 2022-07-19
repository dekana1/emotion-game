from django.shortcuts import render, redirect
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






# user signin 
def signin(request):
    context = {}
    with open("user_data.json") as user_info_json:
        user_info = json.load(user_info_json)

    context['user_info'] = user_info

    print("hey", context['user_info'])

    return render(request, 'signin.html', context)

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

def home(request):
    context = dict()
    context['game_choice'] = game_choice()
    context['word_bag'] = word_bag_generator()

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

        print(game)
        print(word_bank)

        # Convert entry into features and make predictions 

        features = create_feature(user_entry, nrange=(1, 4))
        features = ml_model.vectorizer.transform(features)
        predicted_emotion = model.predict(features)[0]


        predicted_emotion = str(predicted_emotion).capitalize()

        context['result'] = predicted_emotion
        context['game'] = game
        
        # Awarding of stars 

        # if user_entry matches given game sentiment

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
            
        # if user_entry doesn't match sentiment
        else:
            context['result_header'] = random.choice(failure_words)
            context['stars'] = stars

    return render(request, 'result.html', context)

