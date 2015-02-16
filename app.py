import json
import tweepy
from creds import Creds
from user import User

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

# read in words to ignore when calculating most used words from file
def getStopWords():
    stopWords = ['']
    with open("stop_words.txt", "r") as f:
        word = f.readline().strip()
        while word:
            stopWords.append(word)
            word = f.readline().strip()

    return stopWords

# find the time of day the user is most active
def findMostActiveTime(tweets):
    return ""

# find the app the user prefers to tweet from
def findPreferredApp(tweets):
    return ""

# find the ratio of tweets with links to all tweets
def findLinksRatio(tweets):
    return 0.0

# read all tweets and generate a list of most used words
# return the top 10
def findMostUsedWords(tweets, stopWords):
    words = {}
    for tweet in tweets:
        newWords = tweet.text.strip().split(" ")
        
        for newWord in newWords:
            lower = newWord.lower()
            if lower not in stopWords:
                if lower not in words:
                    words[lower] = 1
                else:
                    words[lower] += 1

    sortedWords = sorted(words, key=words.get, reverse=True)
    return sortedWords[:10]

# calculate a 'happiness' level for a user
# -1 = very unhappy, 1 = very happy
def findHappiness(tweets):
    return 0.0

# get information about a user, such as
#   time of day user is most active
#   app user prefers to send tweets from
#   friend/follower count
#   ratio of tweets with links to total tweets
#   user's top 10 most used words
def analyzeUser(user, stopWords):
    userJSON = {'id' : user.id}

    userInfo = {'name' : user.name,
                'screen_name' : user.screen_name,
                'friends' : user.friends_count,
                'followers' : user.followers_count}
    userJSON['user'] = userInfo

    tweets = getAllTweets(user.id)

    analysisInfo = {}
    analysisInfo['timeMostActive'] = findMostActiveTime(tweets)
    analysisInfo['preferredApp'] = findPreferredApp(tweets)
    analysisInfo['linksRatio'] = findLinksRatio(tweets)
    analysisInfo['topTenWords'] = findMostUsedWords(tweets, stopWords)
    analysisInfo['happiness'] = findHappiness(tweets)
    userJSON['analysis'] = analysisInfo

    print json.dumps(userJSON, indent=4)

# main
if __name__ == "__main__":
    DEBUG = True
    CLASSES = False

    api = login()

    if CLASSES:
        with open("classes.txt", "w+") as f:
            user = api.get_user("@VanessaHudgens")
            tweet = api.user_timeline(user.id, count=1)[0]
            
            f.write("User:\n")
            for attr in dir(user):
                f.write("\t" + attr + "\n")

            f.write("\nTweet:\n")
            for attr in dir(tweet):
                f.write("\t" + attr + "\n")

    stopWords = getStopWords()
    if DEBUG:
        analyzeUser(getUsers()[2], stopWords)
    else:
        for user in getUsers():
            analyzeUser(user, stopWords)