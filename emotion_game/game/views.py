from django.shortcuts import render
import math
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from model.model import create_feature
import pickle
# Create your views here.

model = pickle.load(open('model.pkl', 'rb+'))
vectorizer = DictVectorizer(sparse=True)


def home(request):

    return render(request, 'home.html')


def predictor(request):
    if request.method == 'POST':
        temp = dict()

        user_entry = request.POST.get('user_entry')

        features = create_feature(user_entry, nrange=(1, 4))
        features = vectorizer.transform(features)

        predicted_emotion = model.predict(user_entry)[0]

        return render(request, 'result.html', {'result': predicted_emotion})

