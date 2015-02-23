# tweelings
an app that analyzes how the Internet affects people's feelings, using the Twitter API

I apologize for the stupid name

###USAGE
   to analyze a single user:

      `tweelings [-OPTION] [PATHNAME] -u <USERNAME>`

   to analyze a list of users from a file:

      `tweelings [-OPTION] [PATHNAME] -U <USERFILE>`

   options:

      note: all options must come before the -u/-U flags and their associated targets.

      -S <PATHNAME> 
         specify a file containing a list of stop words. Stop
         words are words that should be skipped in analysis,
         such as 'the' or 'I'. By default, tweelings uses the
         list of stop words in default/stopwords_default.txt.

      -H <PATHNAME>
         specify a JSON file containing a list of words and
         their related happiness values. By default, tweelings
         uses the list of words/happiness values in
         default/happywords_default.json.

      -o <PATHNAME>
         specify a file to write output to. By default,
         tweelings outputs to stdout.

###DESCRIPTION

I knew that I wanted to use Python to accomplish the task, and after some research, I decided 
on using the Tweepy library, which is essentially a set of bindings to the Twitter API.
The Tweepy docs can be found at http://tweepy.readthedocs.org/en/v3.2.0/

I started out writing this as a simple script, but I realized that I had a lot of data to keep track of, so I decided to make a class called Tweelings. The Tweelings class will be described below.

```
class Tweelings:

   def __init__():
      When the object is first created, it logs in using the keys I created. It also
      initalizes some empty lists, users and userAnalyses, which will be used later.
      It then defines the default stop words and happy words, which can be found in
      the defaults directory. Finally, it sets the output file to None, which can be
      changed via a command line argument. 

   def login():
      Logs into Twitter using my keys and returns the tweepy.api object.

   def setStopWords(stopWordsFile):
      Sets the stopwords to be used when analyzing tweets. Stop words are words that
      you woudln't want to use in analysis because they don't really contribute much
      to the overall meaning of the text, such as "the" or "I". The default list of
      stopwords can be found in defaults/stopwords_default.txt

   def setOutputFile(outputFile):
      Sets the file where the output will be written to. This can be set using the
      -o flag from the command line.

   def getUsers(usersFile):
      Gets and returns a list of usernames from the specified file. This is called
      using the -U flag from the command line.

   def getTweets(id, max):
      Gets as many tweets as possible from a user specified by id. The Twitter API
      only allows 200 tweets to be retrieved at a time, so I found an algorithm that
      retrieves all tweets in increments of 200. The algorithm works by getting the
      first 200 tweets and remembering the id of the oldest one in a variable called
      oldest. Tweets are retrieved using the tweepy.api.user_timeline() method,
      which takes an argument max_id, which is just (oldest - 1). This occurs until
      the user_timeline() method returns the empty list. Credit for this algorithm
      goes to github user yanofsky.
```
      The script can be found at https://gist.github.com/yanofsky/5436496
```

   def setHappyWords(happywordsFile):
      Reads in a list of words and their happiness weights from the specified file.
      The default list of happywords and their weights can be found in defaults/happywords_default.json.
```
      This default file is a compact version of a file that can be found at
      http://hedonometer.org/api/v1/words/?format=json
```

   def findHappiness(wordFreqs):
      Uses a dict of words and their respective frequencies to determine a user's
      associated happiness level. It works by multiplying a given word's happiness
      value by it's frequency. These products are summed together and then divided
      by the sum of all the word frequencies. This number is in (1, 9), so it is
      mapped to (-1, 1) before being returned. This algorithm was originally
      developed in [1], and further improved in [2].

   def _analyzeUser(id):

   def analyzeUser(id):
      A wrapper for _analyzeUser(). This method returns a JSON object representing
      all of the data returned by _analyzeUser().

   def analyzeUsers(usersFile):
      Returns a JSON object containing the output of _analyzeUser() for all users
      in the specified usersFile.

   def showHelp():
      Displays how to use Tweelings.

   def _map(x):
      A utility function that maps a number in (1, 9) to (-1, 1). It can be used
      to map numbers to/from other ranges as well, but Tweelings always uses the
      defaults.

   def _byteify(input):
      A utility function that recursively encodes an input object to unicode,
      specifically UTF-8.
```
      Credit goes to StackOverflow user Mark Amery.
      The code can be found at http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python#13105359
```

   def main():
      Handles command line arguments and calls the correct functions. See USAGE.
   ```

###CITATIONS
   1. Dodds PS, Danforth CM (2009) Measuring the happiness of large-scale written expression: Songs, blogs, and presidents. Journal of Happiness Studies.

   2. Dodds PS, Harris KD, Kloumann IM, Bliss CA, Danforth CM (2011) Temporal Patterns of Happiness and Information in a Global Social Network: Hedonometrics and Twitter. PLoS ONE 6(12): e26752. doi:10.1371/journal.pone.0026752