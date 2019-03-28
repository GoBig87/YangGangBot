import praw
from datetime import datetime
import mongoengine
import time
from threading import Thread

# my imports
from RedditCrawler import RedditCrawler

#This Class is the mongoDB structure
class Post(mongoengine.Document):
    Platform = mongoengine.StringField(default="Reddit")
    PostID   = mongoengine.StringField(required=True)
    PostStatus = mongoengine.IntField(default=0)

#Maybe we should archive posts after theyve been posted?
class Archive(mongoengine.Document):
    Platform = mongoengine.StringField(default="Reddit")
    PostID   = mongoengine.StringField(required=True)
    PostStatus = mongoengine.IntField(default=0)

class RedditBot():
    def __init__(self):
        # From mongoengine, connects to DB
        mongoengine.connect('yang_database')
        self.subreddits = ['politics','democrats','PoliticalHumor']
        self.platforms  = ["Twitter","RSS"]
        self.currentPostID = ''
        self.currentDate = (datetime.fromtimestamp(time.time())).strftime('%m %d %Y')
        self.reddit = praw.Reddit(client_id="soXdD-RwcsgTPA",
                             client_secret='BWLl9zDrpDrDDFc-OUqKYd-AD84',
                             user_agent='The Yang Gang Bot',
                             username='TheYangGangBot',
                             password= 'securethebag')

    # This function needs to run once a day
    def makePost(self):
        print("RedditBot: Making Daily Post")
        postTitle = "The Daily Andrew Yang Run Down %s " % self.currentDate

        text = 'This post is a megapost that gets updated through ' \
               'out the day whenever u/TheYangGangBot finds ' \
               'information on the internet and social media.' \
               ' When the bot finds information it will make a '\
               'comment in this post linking to the information.'

        submission = self.reddit.subreddit('testingground4bots').submit(postTitle, selftext=text)
        self.currentPostID = submission.id
        print("RedditBot: Daily Post Made")

    # Function to Place post url's in the current posts comment with the
    # matching subreddit
    def makeSubRedditComment(self,postID):
        currentSubmission = self.reddit.submission(id=self.currentPostID)
        postSubmission = self.reddit.submission(id=postID)
        #Cycle through top level comments to find the right section to reply
        found = False
        for comment in currentSubmission.comments:
            # Check to make sure the comment is TheYangGangBot and the comment contains the subreddit
            if comment.author == "TheYangGangBot" and str(postSubmission.subreddit).upper() in comment.body.upper():
                url = " https://np.reddit.com"+postSubmission.permalink
                comment.reply(url)
                print("RedditBot: Making comment %s" % url)
                found = True
        if not found:
            comment = currentSubmission.reply("Posts from %s" % postSubmission.subreddit)
            url = " https://np.reddit.com" + postSubmission.permalink
            print("RedditBot: Making comment %s" % url)
            time.sleep(10)
            comment.reply(url)

    def makeTwitterComment(self):
        pass

    def searchDatabase(self):
        # searches all the posts in the database
        for post in Post.objects:
            if post.PostStatus == 0:
                if post.Platform == "Reddit":
                    print("RedditBot: Reddit Post Found")
                    self.makeSubRedditComment(post.PostID)
                    post.update(PostStatus = 1)
                if post.Platform == "Twitter":
                    self.makeTwitterComment()

    # Run this function forever
    def run(self):
        rc = RedditCrawler()
        thread = Thread(target=rc.runCrawler)
        thread.start()
        while True:
            print("RedditBot: Strarting Reddit bot")
            if self.currentPostID == "":
                self.makePost()
            if self.currentDate != (datetime.fromtimestamp(time.time())).strftime('%m %d %Y'):
                self.makePost()
                self.currentDate = (datetime.fromtimestamp(time.time())).strftime('%m %d %Y')
            else:
                print("RedditBot: Searching DataBase")
                self.searchDatabase()
            print("RedditBot: Sleeping 15 minutes")
            time.sleep(900)
        rc.running = False

# unit test
if __name__ == "__main__":
    rb =  RedditBot()
    rb.run()