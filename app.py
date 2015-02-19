"""
TODO

time zones?
links ratio

keep frequencies with 'most' statistics
"""

import json
import time
import tweepy
from tweepy.error import TweepError
from creds import Creds
from user import User
from sys import argv, exit

DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# login to the twitter API using the Creds class
def login():
    creds = Creds()

    auth = tweepy.OAuthHandler(creds.c_key, creds.c_secret)
    auth.set_access_token(creds.a_token, creds.a_secret)

    return tweepy.API(auth)

# read in users from file
def getUsers():
    f = open("users.txt", "r")

    users = []
    id = f.readline().strip()
    while id:
        users.append(api.get_user(id))
        id = f.readline().strip()

    f.close()
    return users

# read in words to ignore when calculating most used words from file
def getStopWords():
    stopWords = ['']
    with open("stop_words.txt", "r") as f:
        word = f.readline().strip()
        while word:
            stopWords.append(word)
            word = f.readline().strip()

    return stopWords

# get as many tweets from a user as possible
# twitter API only allows 200 per request, so make multiple
# max 3200 tweets can be retrieved
def getAllTweets(id):
    tweets = []
    new_tweets = api.user_timeline(id, count=200, include_rts=True)
    tweets.extend(new_tweets)
    oldest = tweets[-1].id - 1
    while len(new_tweets) > 0:
        new_tweets = api.user_timeline(id, max_id=oldest, count=200, include_rts=True)
        tweets.extend(new_tweets)
        oldest = tweets[-1].id - 1

    return tweets

# get information about a user, such as
#   total tweet count
#   time user is most active
#   preferred app
#   friend/follower count
#   link ratio
#   most used words
#   most favorited/retweeted tweets
def analyzeUser(user):
    try:
        tweets = getAllTweets(user.id)
        userJSON = {}

        userInfo = {'id' : user.id,
                    'name' : user.name,
                    'screen_name' : user.screen_name,
                    'friends' : user.friends_count,
                    'followers' : user.followers_count}
        userJSON['user'] = userInfo

        # dict to hold all analysis info
        analysisInfo = {'tweets_retrieved' : len(tweets)}

        # most favorited tweet
        mostFavorited = tweets[0]

        # most retweeted tweet
        mostRetweeted = None
        mostRetweets = 0

        # dict of sources/frequencies
        sources = {}

        # dict of words/frequencies
        wordFreqs = {}

        # dict of active times
        timeFreqs = {'early_morning' : 0, #  4:00AM -  6:59AM
                     'morning'       : 0, #  7:00AM - 11:59AM
                     'afternoon'     : 0, # 12:00PM -  4:59PM
                     'evening'       : 0, #  7:00PM - 11:59PM
                     'late_night'    : 0} # 12:00AM -  3:59AM

        for tweet in tweets:
            # split the tweet into words
            # filter out stopwords
            words = tweet.text.strip().split(" ")

            # make sure the tweet is authored by the user
            if "RT" not in words:
                # keep track of word use
                for word in words:
                    lower = word.lower()
                    if lower not in stopWords:
                        if lower not in wordFreqs:
                            wordFreqs[lower] = 1
                        else:
                            wordFreqs[lower] += 1

                # find most retweeted original tweet
                if tweet.retweet_count > mostRetweets:
                    mostRetweeted = tweet
                    mostRetweets = tweet.retweet_count

            # find most favorited tweet
            if tweet.favorite_count > mostFavorited.favorite_count:
                mostFavorited = tweet

            # find the time of day the user is most active
            hour = time.strptime(str(tweet.created_at), DATEFORMAT).tm_hour
            if hour < 4:
                timeFreqs['late_night'] += 1
            elif hour >= 4 and hour < 7:
                timeFreqs['early_morning'] += 1
            elif hour >= 7 and hour < 12:
                timeFreqs['morning'] += 1
            elif hour >= 12 and hour < 17:
                timeFreqs['afternoon'] += 1
            elif hour >= 17:
                timeFreqs['evening'] += 1 

            # find the app the user prefers to tweet from
            newSource = tweet.source
            if newSource not in sources:
                sources[newSource] = 1
            else:
                sources[newSource] += 1

            # find the ratio of tweets with links to all tweets


            # find the user's happiness on a scale of -1 to 1
            # -1 = very unhappy, 1 = very happy

        # add mostFavorited to JSON
        mostFavoritedInfo = {'id' : mostFavorited.id,
                             'text' : mostFavorited.text,
                             'favorite_count' : mostFavorited.favorite_count}
        analysisInfo['mostFavorited'] = mostFavoritedInfo

        # add mostRetweeted to JSON
        mostRetweetedInfo = {'id' : mostRetweeted.id,
                             'text' : mostRetweeted.text,
                             'retweet_count' : mostRetweeted.retweet_count}
        analysisInfo['mostRetweeted'] = mostRetweetedInfo

        # analyze time frequencies to find most active time
        mostActiveTime, most = "", 0
        for activeTime, freq in timeFreqs.iteritems():
            if freq > most:
                mostActiveTime, most = activeTime, freq
        analysisInfo['mostActiveTime'] = mostActiveTime

        # analyze sources list to find preferred source
        preferredSource, most = "", 0
        for source, freq in sources.iteritems():
            if freq > most:
                preferredSource, most = source, freq
        analysisInfo['preferredApp'] = preferredSource

        # get the top 10 most used words
        sortedWordFreqs = sorted(wordFreqs, key=wordFreqs.get, reverse=True)
        analysisInfo['mostUsedWords'] = sortedWordFreqs[:10]

        userJSON['analysis'] = analysisInfo

        print json.dumps(userJSON, indent=4)

    except TweepError as te:
        print "Error accessing @%s's account: %s" % (user.screen_name, te)

# main
if __name__ == "__main__":
    stopWords = getStopWords()
    api = login()

    if len(argv) > 1:
        if argv[1] == '-d':
            analyzeUser(getUsers()[2])
        elif argv[1] == '-u':
            analyzeUser(api.get_user(argv[2]))
        else:
            print "invalid syntax."
            exit(0)
    else:
        for user in getUsers():
            analyzeUser(user)