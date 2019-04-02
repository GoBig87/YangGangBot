import tweepy
import Twitter_Handles


class TwitterCrawler():
    def __init__(self):
        consumer_key    = "s3qSyonaSiQZMXE5lM5XhNlgM"
        consumer_secret = "BtGe8Loj1uP7j3TAKSR7WkurNS8AX7d8XghvU8ia9N5HXVVqlZ"
        access_token    = "iEfRYop97bnbpkP8gtaQ9thNXmSKTC"
        access_token_secret = "EvxGLeGQnb895AlOxeLvtrBierVJPJcv5XkB4SOLs37q"
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        self.api = tweepy.API(auth)

    def searchTweets(self):

        public_tweets = self.api.home_timeline()
        for tweet in public_tweets:
            print
            tweet.text


if __name__ == "__main__":
    tc = TwitterCrawler()