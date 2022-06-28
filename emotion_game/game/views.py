from django.shortcuts import render
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


def evaluate_entry(user_entry, word_bag):
    words_used_count = 0
    words_used_user_list = list()
    for word in str(user_entry).split():
        if word in word_bag:
            words_used_user_list.append(word)
            words_used_count += 1
    if words_used_count == 0:
        return "You didn't use any words!"
    else:
        return words_used_user_list, len(words_used_user_list)


def home(request):
    context = dict()
    context['game_choice'] = game_choice()
    context['word_bag'] = word_bag_generator()

    return render(request, 'home.html', context)


def predictor(request):
    if request.method == 'POST':

        user_entry = request.POST.get('user_entry')
        print(user_entry)
        features = ml_model.create_feature(user_entry, nrange=(1, 4))
        features = ml_model.vectorizer.transform(features)
        predicted_emotion = model.predict(features)[0]
        print(predicted_emotion)

        return render(request, 'result.html', context={'result': predicted_emotion})

