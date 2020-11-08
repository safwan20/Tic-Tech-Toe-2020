import pandas as pd
import numpy as np
import html
import string
import re
import spacy
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
from textblob import TextBlob

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nlp = spacy.load('en_core_web_sm')
stopword = nltk.corpus.stopwords.words('english')
wn = nltk.WordNetLemmatizer()

# CHANGE THESE PATHS
cv = pickle.load(open('static/model/cv.pkl', 'rb'))
abusive = pickle.load(open('static/model/abusive_model.sav', 'rb'))
hate = pickle.load(open('static/model/hate_speech_model.sav', 'rb'))


def preprocess(text):
    text = "".join([char for char in text if char not in string.punctuation])
    text = re.sub('[0-9]+', '', text)
    text = re.split('\W+', text)
    text = [word for word in text if word not in stopword]
    text = [wn.lemmatize(word) for word in text]
    return text


def pred(inp_dic):
    # Parent Tweet
    if inp_dic['is_reply'] == False:
        text = TextBlob(inp_dic['text'])
        if text.sentiment[0] < 0:
            inp_dic['sentiment'] = 'Negative'
        if text.sentiment[0] == 0:
            inp_dic['sentiment'] = 'Neutral'
        else:
            inp_dic['sentiment'] = 'Positive'
        inp_dic['sentiment_value'] = text.sentiment[0]

    # Replies/Comments
    else:
        text = inp_dic['text']
        text = preprocess(text)
        text = " ".join(text)
        text_feats = cv.transform([text])
        # Hate Speech
        if hate.predict(text_feats)[0] == 0:
            inp_dic['hate_speech'] = 0
        else:
            inp_dic['hate_speech'] = 1

        inp_dic['hate_speech_prob'] = hate.predict_proba(text_feats)[0][1]

        # Abusive Language
        if abusive.predict(text_feats)[0] == 0:
            inp_dic['abusive'] = 0

        else:
            inp_dic['abusive'] = 1

        inp_dic['abusive_prob'] = abusive.predict_proba(text_feats)[0][1]

    return inp_dic
