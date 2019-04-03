import tweepy
import Twitter_Handles
from datetime import datetime
import mongoengine
import time

#This Class is the mongoDB structure
class Post(mongoengine.Document):
    Platform   = mongoengine.StringField(default="Twitter")
    PostID     = mongoengine.StringField(required=True)
    PostAuthor = mongoengine.StringField(required=False)
    PostText   = mongoengine.StringField(required=False)
    PostStatus = mongoengine.IntField(default=0)

class TwitterCrawler():
    def __init__(self):
        self.running = True
        self.e       = ''
        mongoengine.connect('yang_database')
        self.handles    = list(set(Twitter_Handles.handles))
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
            print("TwitterCrawler: Searching %s's tweets" % handle)
            tmpTweets = None

            try:
                tmpTweets = self.api.user_timeline(handle,tweet_mode="extended")
            except tweepy.TweepError as e:
                self.e = e
                print(self.e)
                while "Rate limit exceeded" in str(self.e):
                    print("TwitterCrawler: Rate Limited Sleeping 60 seconds")
                    time.sleep(60)
                    try:
                        self.e = ''
                        tmpTweets = self.api.user_timeline(handle, tweet_mode="extended")
                    except tweepy.TweepError as e:
                        self.e = e
                        print(self.e)

            if tmpTweets is not None:
                for tweet in tmpTweets:
                    if tweet.created_at.strftime('%m-%d-%Y') == startDate:
                        if "YANG" in tweet.full_text.upper() and "CINDY" not in tweet.full_text.upper() and "PYONGYANG" not in tweet.full_text.upper() :
                           postUrl = "https://twitter.com/"+handle.strip("@")+"/status/"+tweet.id_str
                            # Keep this like \sYANG.  The space weeds out things like Pyongyang
                           if Post.objects(PostID=postUrl):
                                print("TwitterCrawler: Print Post already in DB")
                           else:
                               print("TwitterCrawler: %s" % tweet.full_text)
                               post = Post(PostID=postUrl,PostAuthor=handle,PostText=tweet.full_text)
                               post.save()

        print("TwitterCrawler: Finished Twitter Search")

    def runCrawler(self):
        while self.running:
            self.searchTweets()
            #Sleep 10 minutes between crawls
            print("TwitterCrawler: Sleeping 10 minute")
            time.sleep(600)


if __name__ == "__main__":
    tc = TwitterCrawler()
    tc.searchTweets()