import praw
from datetime import datetime
import mongoengine
import time

#This Class is the mongoDB structure
class Post(mongoengine.Document):
    Platform = mongoengine.StringField(default="Reddit")
    PostID   = mongoengine.StringField(required=True)
    PostStatus = mongoengine.IntField(default=0)

class RedditCrawler():
    def __init__(self):
        #From mongoengine, connects to DB
        mongoengine.connect('yang_database')
        self.subreddits = ['politics','democrats','PoliticalHumor']
        self.reddit = praw.Reddit(client_id="soXdD-RwcsgTPA",
                             client_secret='BWLl9zDrpDrDDFc-OUqKYd-AD84',
                             user_agent='The Yang Gang Bot',
                             username='TheYangGangBot',
                             password= 'securethebag')

    def getPosts(self):
        for subreddit in self.subreddits:
            print(subreddit)
            submissions = self.reddit.subreddit(subreddit).new(limit=1000)
            for submission in submissions:
                ts = submission.created - 4*3600 # GMT time is 4 hours ahead, subtract 4 hours to get EST
                postDate = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                currentDate =datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
                if postDate == currentDate:
                   currentSubmission = submission.title.upper()
                   if "YANG" in submission.title.upper():
                       if Post.objects(PostID=submission.id).count():
                            print("Print Post already in DB")
                       else:
                           print(currentSubmission)
                           post = Post(PostID=submission.id)
                           post.save()
                else:
                    #Posts are no longer from today
                    break


    def run(self):
        while True:
            self.getPosts()
            #Sleep 10 minutes between crawls
            time.sleep(600)

# unit test
if __name__ == "__main__":
    rc =  RedditCrawler()
    rc.run()