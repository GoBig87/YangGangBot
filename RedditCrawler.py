import praw
import datetime
from mongoengine import *

#This Class is the mongoDB structure
class Post(Document):
    Platform = StringField(default="Reddit")
    PostID   = StringField(required=True)
    PostStatus = IntField(default=0)

class RedditCrawler():
    def __init__(self):
        #From mongoengine, connects to DB
        connect('yang_database')
        self.subreddits = []
        self.reddit = praw.Reddit(client_id="INSERT ID HERE",
                             client_secret='INSERT CLIENT KEY HERE',
                             user_agent='The Yang Gang Bot',
                             username='TheYangGangBot',
                             password= 'securethebag')

    def getPosts(self):
        for subreddit in self.subreddits:
            submissions = self.reddit.subreddit(subreddit).new(limit=1000)
            for submission in submissions:
                time = submission.created
                date = datetime.datetime.fromtimestamp(time)
                #Need to fix, unsure of date format from reddit
                if date == datetime.datetime.today().strftime('%Y-%m-%d'):
                   if "YANG" in submission.title.upper():
                       if Post.objects(PostID=submission.id).count():
                           #This shouldn't happen
                            print("Print Error Post already in DB")
                       else:
                           # Create new Post in mongodb
                           post = Post(PostID=submission.id)
                           post.save()
                else:
                    #Posts are no longer from today
                    break
            else:
                # Continue if the inner loop wasn't broken.
                continue
            # Inner loop was broken, break the outer.
            break


