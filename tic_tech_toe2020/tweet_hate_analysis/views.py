from django.shortcuts import render
from tic_tech_toe2020.local_settings import *
import tweepy
import json
from . import pred
from textblob import TextBlob


def get_polarity(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity


def get_twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def home(request):
    return render(request, 'home.html')


def dashboard(request):
    tweet_url = request.POST['url']
    split_tweet = tweet_url.split('/')
    handle, tweet_id = split_tweet[-3], split_tweet[-1]

    api = get_twitter_api()

    replies = []
    for tweet in tweepy.Cursor(
            api.search, q='to:@' + handle,
            result_type='recent',
            timeout=999999).items(1000):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str == tweet_id):
                replies.append(tweet)

    negative = 0
    results = []
    for reply in replies:
        reply_dict = reply.__dict__
        data_dict = {
            'is_reply': True,
            'username': handle,
            'text': reply_dict.get('text'),
            'date_time': reply_dict.get('created_at')
        }
        result = pred.pred(data_dict)
        results.append(result)
        negative += result['hate_speech_prob']

    negative /= len(replies)

    tweet_text = api.get_status(tweet_id).text
    tweet_positive = (get_polarity(tweet_text) + 1)/2

    tweets_hate_by_date = {}
    tweets_total_by_date = {}
    for result in results:
        date_time, hate_speech_prob = result['date_time'], result['hate_speech_prob']
        if date_time.date() in tweets_hate_by_date:
            tweets_hate_by_date[date_time.date(
            )] += int(hate_speech_prob > 0.5)
        else:
            tweets_hate_by_date[date_time.date()] = int(hate_speech_prob > 0.5)

        if date_time.date() in tweets_total_by_date:
            tweets_total_by_date[date_time.date()] += 1
        else:
            tweets_total_by_date[date_time.date()] = 1

    bar_data = [['Date', 'Non-hate', 'Hate']]
    for date in tweets_hate_by_date:
        bar_data.append([str(date),
                         tweets_total_by_date[date] - tweets_hate_by_date[date], tweets_hate_by_date[date]])

    context = {
        'tweet_text': tweet_text,
        'reply_negative_percent': negative * 100,
        'reply_positive_percent': (1 - negative) * 100,
        'tweet_positive_percent': tweet_positive * 100,
        'tweet_negative_percent': (1 - tweet_positive) * 100,
        'bar_data': json.dumps(bar_data)
    }

    return render(request, 'dashboard.html', context)
