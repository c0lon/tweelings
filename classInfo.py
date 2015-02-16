# get the class attributes of twitter objects

import tweepy
from creds import Creds

def login():
    creds = Creds()

    auth = tweepy.OAuthHandler(creds.c_key, creds.c_secret)
    auth.set_access_token(creds.a_token, creds.a_secret)

    return tweepy.API(auth)

if __name__ == '__main__':
    api = login()

    with open("classes.txt", "w+") as f:
        user = api.get_user("@VanessaHudgens")
        tweet = api.user_timeline(user.id, count=1)[0]
        
        f.write("User:\n")
        for attr in dir(user):
            f.write("\t" + attr + "\n")

        f.write("\nTweet:\n")
        for attr in dir(tweet):
            f.write("\t" + attr + "\n")