import tweepy
from creds import Creds
from user import User

def login():
    creds = Creds()

    auth = tweepy.OAuthHandler(creds.c_key, creds.c_secret)
    auth.set_access_token(creds.a_token, creds.a_secret)

    return tweepy.API(auth)

def getUsers():
    f = open("users.txt", "r")

    users = []
    id = f.readline().strip()
    while id:
        users.append(api.get_user(id))
        id = f.readline().strip()

    f.close()
    return users

api = login()
users = getUsers()

for user in users:
    print user.id
    print user.name
    print user.screen_name
    print ""

public_tweets = api.home_timeline()
for tweet in public_tweets:
   print tweet.text
