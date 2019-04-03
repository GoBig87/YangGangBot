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

class UserCount(mongoengine.Document):
    Month = mongoengine.IntField(default=0)
    Day   = mongoengine.IntField(default=0)
    Year  = mongoengine.IntField(default=0)
    Hour  = mongoengine.IntField(default=0)
    Min   = mongoengine.IntField(default=0)
    count = mongoengine.IntField(default=0)

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

        # Catches rate limit error
        try:
            submission = self.reddit.subreddit('YangForPresidentHQ').submit(postTitle, selftext=text)
        except praw.exceptions.APIException as e:
            if e.error_type == "RATELIMIT":
                print("RedditBot: Ratelimited, %s" % e.message)
                wait_time = e.message.strip('you are doing that too much. try again in ').strip('.').split(' ')
                if wait_time[1] == 'seconds':
                    time.sleep(int(wait_time[0])+2)
                else:
                    time.sleep(int(wait_time[0])*60+60)
                print("RedditBot: Retrying post")
                submission = self.reddit.subreddit('testingground4bots').submit(postTitle, selftext=text)
            else:
                print(e)
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
            commentSearchStr = ' ' + str(postSubmission.subreddit).upper()
            if comment.author == "TheYangGangBot" and  commentSearchStr in comment.body.upper():
                url = " https://np.reddit.com"+postSubmission.permalink
                self.sendPrawCommand(comment.reply, url)
                print("RedditBot: Making comment %s" % url)
                found = True
        if not found:
            reply = "Posts from %s" % postSubmission.subreddit
            comment = self.sendPrawCommand(currentSubmission.reply,reply)
            url = " https://np.reddit.com" + postSubmission.permalink
            print("RedditBot: Making comment %s" % url)
            self.sendPrawCommand(comment.reply,url)

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
                    print("RedditBot: Tweet Found")
                    self.makeTwitterComment()
                    post.update(PostStatus=1)

    def getActiveUsers(self):
        timeList = datetime.fromtimestamp(time.time()).strftime('%m:%d:%Y:%H:%M').split(':')
        usercount = UserCount(Month=timeList[0],Day=timeList[1],Year=timeList[2],Hour=timeList[3],Min=timeList[4])
        usercount.save()
        subreddit = self.reddit.subreddit('YangForPresidentHQ')
        active_users = int(subreddit.active_user_count)
        print("RedditBot: Active users in YangForPresidentHQ %i" % active_users)
        usercount.update(count=active_users)

    def sendPrawCommand(self,command,input):
        try:
            return command(input)
        except praw.exceptions.APIException as e:
            if e.error_type == "RATELIMIT":
                print("RedditBot: Ratelimited, %s" % e.message)
                wait_time = e.message.strip('you are doing that too much. try again in ').strip('.').split(' ')
                if wait_time[1] == 'seconds':
                    time.sleep(int(wait_time[0])+2)
                else:
                    time.sleep(int(wait_time[0])*60+60)
                print("RedditBot: Retrying PRAW command")
                return command(input)
            else:
                print(e)

    # Run this function forever
    def run(self):
        rc = RedditCrawler()
        thread = Thread(target=rc.runCrawler)
        thread.start()
        while True:
            try:
                print("RedditBot: Strarting Reddit bot")
                if self.currentPostID == "":
                    self.makePost()
                if self.currentDate != (datetime.fromtimestamp(time.time())).strftime('%m %d %Y'):
                    print("RedditBot: Starting a new Day!")
                    self.currentDate = (datetime.fromtimestamp(time.time())).strftime('%m %d %Y')
                    self.makePost()
                else:
                    print("RedditBot: Searching DataBase")
                    self.searchDatabase()
                    self.getActiveUsers()

                print("RedditBot: Sleeping 15 minutes")
                time.sleep(900)
            except:
                pass
        rc.running = False

# unit test
if __name__ == "__main__":
    rb =  RedditBot()
    rb.run()