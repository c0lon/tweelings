import tweepy
from creds import Creds
from user import User

def login():
    creds = Creds()

    auth = tweepy.OAuthHandler(creds.c_key, creds.c_secret)
    auth.set_access_token(creds.a_token, creds.a_secret)

    return tweepy.API(auth)

api = login()

tweets = []
new_tweets = api.user_timeline("@c0lon", count=200)
tweets.extend(new_tweets)
oldest = tweets[-1].id - 1
while len(new_tweets) > 0:
    new_tweets = api.user_timeline("@c0lon", max_id=oldest, count=200)
    tweets.extend(new_tweets)
    oldest = tweets[-1].id - 1

print len(tweets)