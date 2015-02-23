# tweelings
an app that analyzes how the Internet affects people's feelings, using the Twitter API

I apologize for the stupid name

###DESCRIPTION

I knew that I wanted to use Python to accomplish the task, and after some research, I decided 
on using the Tweepy library, which is essentially a set of bindings to the Twitter API.
The Tweepy docs can be found at http://tweepy.readthedocs.org/en/v3.2.0/

I started out writing this as a simple script, but I realized that I had a lot of data to keep track of, so I decided to make a class called Tweelings. The Tweelings class will be described below.

class Tweelings

   `def __init__():`
      When the object is first created, it logs in using the keys I created. It also initalizes some empty lists, users and userAnalyses, which will be used later. It then defines the default stop words and happy words, which can be found in the defaults directory. Finally, it sets the output file to None, which can be changed via a command line argument. 

   `def login():`
      When the object is first created, it logs in using the keys I created. It also initalizes some empty lists, users and userAnalyses, which will be used later. It then defines the default stop words and happy words, which can be found in the defaults directory. Finally, it sets the output file to None, which can be changed via a command line argument. 

   `def loing():`
      Logs into Twitter using my keys and returns the tweepy.api object.

   `def setStopWords(stopWordsFile):`
      Sets the stopwords to be used when analyzing tweets. Stop words are words that you woudln't want to use in analysis because they don't really contribute much to the overall meaning of the text, such as "the" or "I". The default list of stopwords can be found in defaults/stopwords_default.txt

   `def setOutputFile(outputFile):`
      Sets the file where the output will be written to. This can be set using the -o flag from the command line.

   `def getUsers(usersFile):`
      Gets and returns a list of usernames from the specified file. This is called using the -U flag from the command line.

   `def getTweets(id, max):`
      Gets as many tweets as possible from a user specified by id. The Twitter API only allows 200 tweets to be retrieved at a time, so I found an algorithm that retrieves all tweets in increments of 200. The algorithm works by getting the first 200 tweets and remembering the id of the oldest one in a variable called oldest. Tweets are retrieved using the
      tweepy.api.user_timeline() method, which takes an argument max_id, which is just
      (oldest - 1). This occurs until the user_timeline() method returns the empty list.
      Credit for this algorithm goes to github user yanofsky.
      The script can be found at https://gist.github.com/yanofsky/5436496

   `def setHappyWords(happywordsFile):`
      Reads in a list of words and their happiness weights from the specified file. The default list of happywords and their weights can be found in defaults/happywords_default.json. This default file is a compact version of a file that can be found at
      http://hedonometer.org/api/v1/words/?format=json

   `def findHappiness(tweet):`
