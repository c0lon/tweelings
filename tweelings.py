#!/usr/bin/env python

import json
import tweepy
from time import strptime
from tweepy.error import TweepError
from sys import argv, exit

class Tweelings(object):

    # format string for dates
    DATEFORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self):
        self.login()
        self.users = []
        self.userAnalyses = []

        self.setStopWords()
        self.setHappyWords()

        self.outputFile = None

    #
    # login to the twitter API using the Creds class
    def login(self):
        c_key = "V7Nw0tT3dps5qlo7ICoWE1uI6"
        c_secret = "NHEVWdnpsagNvlpgWITdMCvmoXGSn6Hfkb2hYnfBXDH2laG9xd"

        a_token = "613854165-OqM0QjS2rJsSA2Y0Cq1hnnp0BQ1FPQ7HPrKlEEEZ"
        a_secret = "POi1vDKYE5z89IaZ1K4EjBBEJc5N9gR26wjkTcYi5B7VY"

        auth = tweepy.OAuthHandler(c_key, c_secret)
        auth.set_access_token(a_token, a_secret)

        self.api = tweepy.API(auth)

    #
    # read in words to ignore when calculating most used words from file
    def setStopWords(self, stopWordsFile='defaults/stopwords_default.txt'):
        stopWords = ['']

        try:
            with open(stopWordsFile, 'r') as f:
                word = f.readline().strip()
                while word:
                    stopWords.append(word)
                    word = f.readline().strip()
        except IOError:
            pass

        self.stopWords = stopWords

    #
    # set the output file
    def setOutputFile(self, outputFile):
        self.outputFile = outputFile

    #
    # read in users from file
    def getUsers(self, usersFile):
        users = []

        try:
            with open(usersFile, 'r') as f:
                id = f.readline().strip()
                while id:
                    users.append(self.api.get_user(id))
                    id = f.readline().strip()
        except IOError:
            pass

        return users

    #
    # get as many tweets from a user as possible
    # twitter API only allows 200 per request, so make multiple
    # max 3200 tweets can be retrieved
    def getTweets(self, id, max=0):
        tweets = []

        new_tweets = self.api.user_timeline(id, count=200, include_rts=True)
        tweets.extend(new_tweets)
        oldest = tweets[-1].id - 1
        while len(new_tweets) > 0:
            new_tweets = self.api.user_timeline(id, max_id=oldest, count=200, include_rts=True)
            tweets.extend(new_tweets)
            oldest = tweets[-1].id - 1

        return tweets

    #
    # get 'happy' words and their happiness scores from file
    def setHappyWords(self, happyWordsFile='defaults/happywords_default.json'):
        happyWords = {}

        try:
            data = open(happyWordsFile)
            happyWords = json.load(data)
        except IOError:
            pass

        self.happyWords = happyWords

    #
    # find a user's happiness level (-1, 1)
    def findHappiness(self, wordFreqs):
        happiness = 0.0
        freqTotal = 0.0

        for word, freq in wordFreqs.iteritems():
            try:
                happiness += self.happyWords[word] * freq
                freqTotal += freq
            except KeyError:
                continue

        return self._map(happiness / freqTotal)

    #
    # get information about a user, such as
    #   total tweet count
    #   time user is most active
    #   preferred app
    #   friend/follower count
    #   link ratio
    #   most used words
    #   most favorited/retweeted tweets
    def _analyzeUser(self, id):
        userJSON = {
            'status' : {
                'error' : False,
                'message' : ''
            }
        }

        try:
            user = self.api.get_user(id)
            tweets = self.getTweets(user.id)

            userInfo = {
                'id'          : user.id,
                'name'        : user.name,
                'screen_name' : user.screen_name,
                'friends'     : user.friends_count,
                'followers'   : user.followers_count
            }
            userJSON['user'] = userInfo

            # dict to hold all analysis info
            analysisInfo = {
                'tweets_retrieved' : len(tweets)
            }

            # most favorited tweet
            mostFavorited = tweets[0]

            # most retweeted tweet
            mostRetweeted = None
            mostRetweets = 0

            # most retweeted original tweet
            mostRetweetedOriginal = None
            mostRetweetsOriginal = 0

            # dict of sources/frequencies
            sources = {}

            # dict of words/frequencies
            wordFreqs = {}

            # dict of active times
            timeFreqs = {
                'early_morning' : 0, #  4:00AM -  6:59AM
                'morning'       : 0, #  7:00AM - 11:59AM
                'afternoon'     : 0, # 12:00PM -  4:59PM
                'evening'       : 0, #  7:00PM - 11:59PM
                'late_night'    : 0  # 12:00AM -  3:59AM
            }

            # count of tweets with links
            linkCount = 0

            # cumulative happiness
            happinessTotal = 0

            for tweet in tweets:
                # split the tweet into words
                # filter out stopwords
                words = tweet.text.strip().split(" ")

                # make sure the tweet is authored by the user
                if "RT" not in words:
                    # keep track of word use
                    for word in words:
                        lower = word.lower()
                        if lower not in self.stopWords:
                            if lower not in wordFreqs:
                                wordFreqs[lower] = 1
                            else:
                                wordFreqs[lower] += 1

                    # find most retweeted original tweet
                    if tweet.retweet_count > mostRetweetsOriginal:
                        mostRetweetedOriginal = tweet
                        mostRetweetsOriginal = tweet.retweet_count

                #
                # find most retweeted tweet
                if tweet.retweet_count > mostRetweets:
                    mostRetweeted = tweet
                    mostRetweets = tweet.retweet_count

                #
                # find most favorited tweet
                if tweet.favorite_count > mostFavorited.favorite_count:
                    mostFavorited = tweet

                #
                # find the time of day the user is most active
                hour = strptime(str(tweet.created_at), self.DATEFORMAT).tm_hour
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

                #
                # find the app the user prefers to tweet from
                newSource = tweet.source
                if newSource not in sources:
                    sources[newSource] = 1
                else:
                    sources[newSource] += 1

                #
                # keep track of tweets with links in them
                linkCount += len(tweet.entities['urls'])

            #
            # add mostFavorited to JSON
            mostFavoritedInfo = {
                'id'             : mostFavorited.id,
                'text'           : mostFavorited.text,
                'favorite_count' : mostFavorited.favorite_count
            }
            analysisInfo['mostFavorited'] = mostFavoritedInfo

            #
            # add mostRetweeted to JSON
            mostRetweetedInfo = {
                'id'            : mostRetweeted.id,
                'text'          : mostRetweeted.text,
                'retweet_count' : mostRetweeted.retweet_count
            }
            analysisInfo['mostRetweeted'] = mostRetweetedInfo

            #
            # add mostRetweetedOriginal to JSON
            mostRetweetedOriginalInfo = {
                'id'            : mostRetweetedOriginal.id,
                'text'          : mostRetweetedOriginal.text,
                'retweet_count' : mostRetweetedOriginal.retweet_count
            }
            analysisInfo['mostRetweetedOriginal'] = mostRetweetedOriginalInfo

            #
            # analyze time frequencies to find most active time
            mostActiveTime, most = "", 0
            for activeTime, freq in timeFreqs.iteritems():
                if freq > most:
                    mostActiveTime, most = activeTime, freq

            mostActive = {
                'time'       : mostActiveTime,
                'percentage' : (float(most) / len(tweets))
            }
            analysisInfo['mostActiveTime'] = mostActive

            #
            # analyze sources list to find preferred source
            preferred, most = "", 0
            for source, freq in sources.iteritems():
                if freq > most:
                    preferred, most = source, freq

            preferredSource = {
                'source'     : preferred,
                'percentage' : (float(most) / len(tweets))
            }
            analysisInfo['preferredApp'] = preferredSource

            #
            # get the top 10 most used words
            sortedWordFreqs = sorted(wordFreqs, key=wordFreqs.get, reverse=True)
            analysisInfo['mostUsedWords'] = sortedWordFreqs[:10]

            #
            # find ratio of tweets with links
            analysisInfo['linksRatio'] = (float(linkCount) / len(tweets))

            #
            # find average happiness of all tweets analyzes
            analysisInfo['happiness'] = self.findHappiness(wordFreqs)

            #
            # put all analysis info into the JSON dict
            userJSON['analysis'] = analysisInfo

        except TweepError as te:
            userJSON['status'] = {
                'error' : True,
                'message' : te.message
            }

        finally:
            return userJSON
    #
    # wrapper for analyze user
    def analyzeUser(self, id):
        result = self._byteify(self._analyzeUser(id))

        if self.outputFile:
            with open(self.outputFile, 'w+') as outfile:
                json.dump(result, outfile, indent=4, sort_keys=True, ensure_ascii=False)
        else:
            print json.dumps(result, indent=4, sort_keys=True, ensure_ascii=False)

    #
    # analyze all users in the specified file
    def analyzeUsers(self, usersFile):
        analyses = {}

        self.users = self.getUsers(usersFile)
        for user in self.users:
            analysis = self._analyzeUser(user.id)
            analyses['@'+user.screen_name] = analysis
            self.userAnalyses.append(analysis)

        analyses = self._byteify(analyses)

        if self.outputFile:
            with open(self.outputFile, 'w+') as outfile:
                json.dump(analyses, outfile, indent=4, sort_keys=True)
        else:
            print json.dumps(analyses, indent=4, sort_keys=True)

    def showHelp(self):
        print   """
    tweelings - a simple sociological analytics tool that
    uses the Twitter API.

    usage:
        tweelings [-u] [USER] | [-U] [USERFILE] [-OPTION] [PATHNAME]

    syntax:
      -u <USER>         specify a user to analyze

      -U <PATHNAME>     specify a file containing a list of users to analyze

      -S <PATHNAME>     specify a file containing a list of stop words. Stop
                        words are words that should be skipped in analysis,
                        such as 'the' or 'I'. By default, tweelings uses the
                        list of stop words in default/stopwords_default.txt.
                        Must come before -u or -U

      -H <PATHNAME>     specify a JSON file containing a list of words and
                        their related happiness values. By default, tweelings
                        uses the list of words/happiness values in
                        default/happywords_default.json.
                        Must come before -u or -U

      -o <PATHNAME>     specify a file to write output to. By default,
                        tweelings outputs to stdout.
                        Must come before -u or -U
                """

    #
    # utility function to map happiness levels
    # maps a value from (1, 9) to (-1, 1)
    def _map(self, x, in_min=1, in_max=9, out_min=-1, out_max=1):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    #
    # utility function that encodes objects recursively to unicode
    # this is to avoid the escape sequences that would normally be produced
    def _byteify(self, input):
        if isinstance(input, dict):
            return {self._byteify(key):self._byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [self._byteify(element) for element in input]
        elif isinstance(input,  unicode):
            return input.encode('utf-8')
        else:
            return input

#
# main
# for command line use
def main():
    tweelings = Tweelings()
    result = None

    if len(argv) == 1:
        tweelings.showHelp()
    else:
        try:
            for i in range(1, len(argv)):
                if argv[i] == '-S':
                    tweelings.setStopWords(argv[i+1])
                elif argv[i] == '-H':
                    tweelings.setHappyWords(argv[i+1])
                elif argv[i] == '-o':
                    tweelings.setOutputFile(argv[i+1])
                elif argv[i] == '-u':
                    tweelings.analyzeUser(argv[i+1])
                elif argv[i] == '-U':
                    tweelings.analyzeUsers(argv[i+1])

        except IndexError:
            print "incorrect syntax."
            tweelings.showHelp()

if __name__ == "__main__":
    main()
