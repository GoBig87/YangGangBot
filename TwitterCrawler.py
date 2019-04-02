import tweepy
import Twitter_Handles
from datetime import datetime
import mongoengine
import time

#This Class is the mongoDB structure
class Tweet(mongoengine.Document):
    Platform = mongoengine.StringField(default="Twitter")
    PostID   = mongoengine.StringField(required=True)
    PostStatus = mongoengine.IntField(default=0)

class TwitterCrawler():
    def __init__(self):
        print(len(Twitter_Handles.handles))
        self.handles    = list(set(Twitter_Handles.handles))
        print(len(self.handles))
        consumer_key    = "s3qSyonaSiQZMXE5lM5XhNlgM"
        consumer_secret = "BtGe8Loj1uP7j3TAKSR7WkurNS8AX7d8XghvU8ia9N5HXVVqlZ"
        access_token    = "1112918579551207424-iEfRYop97bnbpkP8gtaQ9thNXmSKTC"
        access_token_secret = "5EvxGLeGQnb895AlOxeLvtrBierVJPJcv5XkB4SOLs37q"
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(auth)

    def searchTweets(self):
        startDate = datetime.fromtimestamp(time.time()).strftime('%m-%d-%Y')
        for handle in self.handles:
            tweets = []
            tmpTweets = self.api.user_timeline(handle,tweet_mode="extended")
            for tweet in tmpTweets:
                if tweet.created_at.strftime('%m-%d-%Y') == startDate:
                    if "YANG" in tweet.full_text.upper():
                        tweets.append(tweet)


if __name__ == "__main__":
    tc = TwitterCrawler()
    tc.searchTweets()