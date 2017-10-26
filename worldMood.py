import time, sys
import auth
import json
import rgbVariable
import wiringpi
import Queue

# Initialize pin numbers
redPin = 20
greenPin = 21
bluePin = 16

# Number of tweets to sample
numberOfTweets = 5000 # 5000

# Initial mood state
state = ""

# Threshold mood change
pDiffLarge = 0.50
pDiffSmall = 0.20

# Alpha value for fast/slow exponential moving averages
fast = 0.25
slow = 0.008

# Initialize queues for each mood
sizeOfQueue = 50000
happyQueue = Queue.Queue(maxsize=sizeOfQueue)
sadQueue = Queue.Queue(maxsize=sizeOfQueue)
surpriseQueue = Queue.Queue(maxsize=sizeOfQueue)
angryQueue = Queue.Queue(maxsize=sizeOfQueue)
loveQueue = Queue.Queue(maxsize=sizeOfQueue)
scaredQueue = Queue.Queue(maxsize=sizeOfQueue)
envyQueue = Queue.Queue(maxsize=sizeOfQueue)

# Define terms for each mood
loveKeywords = ['i love you','i love her','i love him','all my love','i really love','i\'m in love','send love','loving','i love that']
happyKeywords = ['happiest','so happy','so excited','i\'m happy','woot','w00t','so amped','ecstatic','excited to']
surpriseKeywords = ['wow','O_o','can\'t believe','wtf','unbelievable','unreal','sureal','unexpected','sudden','jeez']
angryKeywords = ['i hate','really angry','i am mad','really hate','so angry','livid','i\'m pissed','unfair']
envyKeywords = ['i\'m envious','i\'m jealous','i want to be','why can\'t i','i wish i']
sadKeywords = ['i\'m so sad','i\'m heartbroken','i\'m so upset','i\'m depressed','i can\'t stop crying','heartbroken','tragic','will be missed','will miss']
scaredKeywords = ['i\'m so scared','i\'m really scared','i\'m terrified','i\'m really afraid','so scared i']

# Import the necessary methods from "twitter" library
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

# Variables that contains the user credentials to access Twitter API 
ACCESS_TOKEN = auth.access_token
ACCESS_SECRET = auth.access_token_secret
CONSUMER_KEY = auth.consumer_key
CONSUMER_SECRET = auth.consumer_secret

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

# Initiate the connection to Twitter Streaming API
twitter_stream = TwitterStream(auth=oauth)


def stream(debug=False):
    # Counter to tell us when we've gone through all of our tweets
    tweetCount = numberOfTweets

    # Initially, we have zero of each tweet type
    happyCount = 0
    sadCount = 0
    loveCount = 0
    envyCount = 0
    surpriseCount = 0
    scaredCount = 0
    angryCount = 0

    # Loop through each tweet
    for tweet in iterator:
        tweetCount -= 1
        
        # If we find a keyword in the tweet, increment mood counter
        try:
            text = tweet['text']
            for keyword in happyKeywords:
                    if keyword in tweet['text'].lower():
                        happyCount += 1

            for keyword in sadKeywords:
                    if keyword in tweet['text'].lower():
                        sadCount += 1

            for keyword in loveKeywords:
                    if keyword in tweet['text'].lower():
                        loveCount += 1

            for keyword in envyKeywords:
                    if keyword in tweet['text'].lower():
                        envyCount += 1

            for keyword in angryKeywords:
                    if keyword in tweet['text'].lower():
                        angryCount += 1

            for keyword in scaredKeywords:
                    if keyword in tweet['text'].lower():
                        scaredCount += 1

            for keyword in surpriseKeywords:
                    if keyword in tweet['text'].lower():
                        surpriseCount += 1
        except KeyError as e:
            print(e)
            break
             

        # We've reached the end of our list. Return.
        if tweetCount <= 0:
            print("Happy: "+str(happyCount))
            print("Sad: "+str(sadCount))
            print("Love: "+str(loveCount))
            print("Envy: "+str(envyCount))
            print("Surprise: "+str(surpriseCount))
            print("Scared: "+str(scaredCount))
            print("Angry: "+str(angryCount))
            return happyCount, sadCount, loveCount, envyCount, angryCount, scaredCount, surpriseCount
        
    if debug:
        print("Tweet count: "+str(tweetCount))
        print("Happy: "+str(happyCount))
        print("Sad: "+str(sadCount))
        print("Love: "+str(loveCount))
        print("Envy: "+str(envyCount))
        print("Surprise: "+str(surpriseCount))
        print("Scared: "+str(scaredCount))
        print("Angry: "+str(angryCount))
        print("Iterator: "+str(iterator))
        with open("/home/pi/Documents/WorldMood/moodData/debug", "w") as f:
            f.write(str(tweet))
            f.close()
    return 0,0,0,0,0,0,0
        

def getEMA(sample,a):
    '''
    Returns the exponential moving average of a list
    with alpha parameter a

    Parameters
    ----------
    sample : list
        values for EMA
    a : float
        gives alpha parameter for EMA calculation

    Returns
    -------
    int
        Exponential moving average of sample
    '''

    # Get length of sample
    lengthOfSample = len(sample)

    # Reverse sample (so that we weight new values heaviest)
    sample = list(reversed(sample))

    EMA = 0.0
    for i in  range(0,lengthOfSample):
        EMA = EMA + a*float(sample[i])*(1-a)**(i)
    return EMA

def getPDiff(q):
    '''
    Returns the percent difference between the fast and
    slow expoential moving averages of a list

    Parameters
    ----------
    q : list
        list of values to find difference in fast/slow EMA
        
    Returns
    -------
    int
        difference between fast and slow EMA's (as an irrational number)
    '''

    fastEMA = getEMA(q,fast)
    slowEMA = getEMA(q,slow)
    try:
        return (fastEMA-slowEMA)/slowEMA
    except ZeroDivisionError: # In case we have no data yet for slow EMA
        return 0

def addToQueue(q,n):
    '''
    Adds a number to a queue. If the queue is full, the oldest entry will
    be removed to make room.

    Paramters
    ---------
    q : queue
        queue to add new value to
    n : int
        value to add to queue

    Returns
    -------
    queue
        queue with new value added
    '''
    
    if q.full():
        q.get()
    q.put(n)
    return q

def readMoodData(q,mood):
    '''
    Reads mood data from a file into a queue.

    Paramaters
    ----------
    q : queue
        queue to read mood data into
    mood : str
        which mood should be read into the queue

    Returns
    -------
    queue
        queue with mood data from file
    '''
        
    with open("/home/pi/Documents/WorldMood/moodData/"+mood) as f:
        temp = [x.strip() for x in f.readlines()]
    i = len(temp) - 1
    while i >= 0:
        addToQueue(q,temp[i])
        i -= 1
    return q

def writeMoodData(q,mood):
    '''
    Writes mood data from a queue to a file

    Parameters
    ----------
    q : queue
        queue to read mood data from
    mood : str
        which mood does the queue describe

    Returns
    -------
    Null

    '''
    
    temp = list(q.queue)
    with open("/home/pi/Documents/WorldMood/moodData/"+mood, "w") as f:
        for val in temp:
            f.write("%s\n" % val)
        f.close()

def cleanUp():
    print("Writing queue's...")
    writeMoodData(happyQueue,"happy")
    writeMoodData(sadQueue, "sad")
    writeMoodData(loveQueue, "love")
    writeMoodData(envyQueue, "envy")
    writeMoodData(angryQueue, "angry")
    writeMoodData(scaredQueue, "scared")
    writeMoodData(surpriseQueue, "surprise")
    print("Done.")

    wiringpi.softPwmWrite(redPin,100)
    wiringpi.softPwmWrite(greenPin,100)
    wiringpi.softPwmWrite(bluePin,100)

    
if __name__ == "__main__":
    initialize = True
    while(initialize):
        go = True
        state = "happy"
        rgbVariable.colorChangeSmall("happy","surprise")
        
        # Get a sample of the public data following through Twitter
        iterator = twitter_stream.statuses.sample(language="en")

        # Read mood data into respective queue's
        happyQueue = readMoodData(happyQueue,"happy")
        sadQueue = readMoodData(sadQueue, "sad")
        loveQueue = readMoodData(loveQueue, "love")
        envyQueue = readMoodData(envyQueue, "envy")
        angryQueue = readMoodData(angryQueue, "angry")
        scaredQueue = readMoodData(scaredQueue, "scared")
        surpriseQueue = readMoodData(surpriseQueue, "surprise")
        
        while(go):
            try:
                startTime = time.time()
                numHappy,numSad,numLove,numEnvy,numAngry,numScared,numSurprise = stream()
                if numHappy+numSad+numLove+numAngry+numScared+numSurprise == 0:
                    go = False
                    cleanUp()
                    break
                            
                # Add each value to the queue
                happyQueue = addToQueue(happyQueue,numHappy)
                sadQueue = addToQueue(sadQueue,numSad)
                loveQueue = addToQueue(loveQueue,numLove)
                envyQueue = addToQueue(envyQueue,numEnvy)
                angryQueue = addToQueue(angryQueue,numAngry)
                scaredQueue = addToQueue(scaredQueue,numScared)
                surpriseQueue = addToQueue(surpriseQueue,numSurprise)

                # Calculate % diff for each mood (fast EMA vs slow EMA)
                pDiffHappy = getPDiff(list(happyQueue.queue))
                pDiffSad = getPDiff(list(sadQueue.queue))
                pDiffLove = getPDiff(list(loveQueue.queue))
                pDiffEnvy = getPDiff(list(envyQueue.queue))
                pDiffAngry = getPDiff(list(angryQueue.queue))
                pDiffScared = getPDiff(list(scaredQueue.queue))
                pDiffSurprise = getPDiff(list(surpriseQueue.queue))

                # Find which mood had the greatest shift
                maxDiff = 0
                if pDiffHappy > maxDiff:
                    maxDiff = pDiffHappy
                    state_change = "happy"
                    maxQueue = happyQueue
                if pDiffSad > maxDiff:
                    maxDiff = pDiffSad
                    state_change = "sad"
                    maxQueue = sadQueue
                if pDiffLove > maxDiff:
                    maxDiff = pDiffLove
                    state_change = "love"
                    maxQueue = loveQueue
                if pDiffEnvy > maxDiff:
                    maxDiff = pDiffEnvy
                    state_change = "envy"
                    maxQueue = envyQueue
                if pDiffAngry > maxDiff:
                    maxDiff = pDiffAngry
                    state_change = "angry"
                    maxQueue = angryQueue
                if pDiffScared > maxDiff:
                    maxDiff = pDiffScared
                    state_change = "scared"
                    maxQueue = scaredQueue
                if pDiffSurprise > maxDiff:
                    maxDiff = pDiffSurprise
                    state_change = "surprise"
                    maxQueue = surpriseQueue
                
                # Determine if the change is large enough to change the state or change the lights
                oldState = state
                if state_change != oldState:
                    if maxDiff > pDiffLarge:
                        state = state_change
                        rgbVariable.colorChangeLarge(state,oldState)
                    elif maxDiff > pDiffSmall:
                        state = state_change
                        rgbVariable.colorChangeSmall(state,oldState)

                # Logging stuff...
                print(state.title()+" Fast EMA: "+str(round(getEMA(list(maxQueue.queue),fast),2)))
                print(state.title()+" Slow EMA: "+str(round(getEMA(list(maxQueue.queue),slow),2)))
                print(state.title()+" %Diff = "+str(round(maxDiff*100,1)))
                print("Time to complete: "+str(round(time.time()-startTime,1))+" seconds")
                print("Current queue length: "+str(len(list(happyQueue.queue))))
                print
                f = open('mood', 'a')
                f.write(state+'\n')
                f.close()
                

            except (KeyboardInterrupt):
                cleanUp()
                go = False
                initialize = False
