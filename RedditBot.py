import praw
import datetime
import mongoengine
import time

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
        self.currentDate = datetime.datetime.today().strftime('%m %d %Y')
        self.reddit = praw.Reddit(client_id="soXdD-RwcsgTPA",
                             client_secret='BWLl9zDrpDrDDFc-OUqKYd-AD84',
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

        submission = self.reddit.subreddit('YangForPresidentHQ').submit(postTitle, selftext=text)
        self.currentPostID = submission.id
        #Make Initial Comments to break down subreddits and social media platforms
        for subreddit in self.subreddits:
            time.sleep(10) #Our bot is rate limited ATM
            #self.reddit.submission(id=submission).reply("Posts from r/%s" % subreddit)
            submission.reply("Posts from %s" % subreddit)
        for platform in self.platforms:
            time.sleep(10)  # Our bot is rate limited ATM
            #self.reddit.submission(id=submission).reply("Posts from %s" % subreddit)
            submission.reply("Posts from %s" % platform)

    # Function to Place post url's in the current posts comment with the
    # matching subreddit
    def makeSubRedditComment(self,postID):
        currentSubmission = self.reddit.submission(id=self.currentPostID)
        postSubmission = self.reddit.submission(id=postID)
        #Cycle through top level comments to find the right section to reply
        for comment in currentSubmission.comments:
            # Check to make sure the comment is TheYangGangBot and the comment contains the subreddit
            if comment.author == "TheYangGangBot" and str(postSubmission.subreddit).upper() in comment.body.upper():
                url = " https://np.reddit.com"+postSubmission.permalink
                comment.reply(url)

    def makeTwitterComment(self):
        pass

    def searchDatabase(self):
        # searches all the posts in the database
        for post in Post.objects:
            if post.PostStatus == 0:
                if post.Platform == "Reddit":
                    self.makeSubRedditComment(post.PostID)
                    post.update(PostStatus = 1)
                if post.Platform == "Twitter":
                    self.makeTwitterComment()

    # Run this function forever
    def run(self):
        while True:
            if self.currentPostID == "":
                self.makePost()
            if self.currentDate != datetime.datetime.today().strftime('%m %d %Y'):
                self.makePost()
                self.currentDate = datetime.datetime.today().strftime('%m %d %Y')
            else:
                self.searchDatabase()
                # Sleep 10 minutes
            time.sleep(600)

# unit test
if __name__ == "__main__":
    rb =  RedditBot()
    rb.run()