from django.shortcuts import render
from tic_tech_toe2020.local_settings import *
import tweepy
from . import pred


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
                print(tweet)
                replies.append(tweet)

    '''
    inp_dic={
        is_reply:True,
        username:'mohit',
        text:"chu hai",
        date_time: '4:30',
    }
    '''
    print('REPLIES:')
    for reply in replies:
        reply_dict = reply.__dict__
        data_dict = {
            'is_reply': True,
            'username': handle,
            'text': reply_dict.get('text'),
            'date_time': reply_dict.get('created_at')
        }
        print(data_dict)
        print(pred.pred(data_dict))

    return render(request, 'dashboard.html')
