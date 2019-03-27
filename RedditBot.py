import praw
import datetime
from mongoengine import *
import time

#This Class is the mongoDB structure
class Post(Document):
    Platform = StringField(default="Reddit")
    PostID   = StringField(required=True)
    PostStatus = IntField(default=0)

#Maybe we should archive posts after theyve been posted?
class Archive(Document):
    Platform = StringField(default="Reddit")
    PostID   = StringField(required=True)
    PostStatus = IntField(default=0)

class RedditBot():
    def __init__(self):
        # From mongoengine, connects to DB
        connect('yang_database')
        self.subreddits = ["politics","news","worldnews"]
        self.platforms  = ["Twitter"]
        self.currentPostID = ''
        self.currentDate = datetime.datetime.today().strftime('%m %d %Y')
        self.reddit = praw.Reddit(client_id="INSERT ID HERE",
                             client_secret='INSERT CLIENT KEY HERE',
                             user_agent='The Yang Gang Bot',
                             username='TheYangGangBot',
                             password= 'securethebag')

    # This function needs to run once a day
    def makePost(self):
        postTitle = "The Daily Andrew Yang Run Down %s " % self.currentDate

        text = 'This post is a megapost that gets updated through '
        'out the day whenever u/TheYangGangBot finds '
        'information on the internet and social media.'
        ' When the bot finds information it will make a '
        'comment in this post linking'
        'to the information.'

        submission = self.reddit.submit("YangForPresidentHQ", postTitle, text=text)
        self.currentPostID = submission.id
        #Make Initial Comments to break down subreddits and social media platforms
        for subreddit in self.subreddits:
            submission.add_comment("Posts from %s" % subreddit)
        for platform in self.platforms:
            submission.add_comment("Posts from %s" % platform)

    # Function to Place post url's in the current posts comment with the
    # matching subreddit
    def makeSubRedditComment(self,postID):
        currentSubmission = self.reddit.submission(id=self.currentPostID)
        postSubmission = self.reddit.submission(id=postID)
        #Cycle through top level comments to find the right section to reply
        for comment in currentSubmission.comments:
            if comment.author is "TheYangGangBot" and str(postSubmission.subreddit).upper() is comment.body.upper():
                comment.reply(postSubmission.id_from_url())

    def makeTwitterComment(self):
        pass

    #TODO
    def searchDatabase(self):
        # searches all the posts in the database
        for post in Post.objects:
            if post.PostStatus == 0:
                if post.Platform is "Reddit":
                    if self.makeSubRedditComment(post.PostID):
                        post.update(PostStatus = 1)
                if post.Platform is "Twitter":
                    self.makeTwitterComment()

    # Run this function forever
    def run(self):
        while True:
            if self.currentDate != datetime.datetime.today().strftime('%m %d %Y'):
                self.makePost()
            else:
                self.searchDatabase()

            # Sleep 10 minutes
            time.sleep(600)

# unit test
if __name__ == "__main__":
    rb =  RedditBot()
    rb.run()