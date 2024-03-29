import praw
from datetime import datetime
import mongoengine
import time
from threading import Thread

# my imports
from RedditCrawler import RedditCrawler
from TwitterCrawler import TwitterCrawler
from YahooCrawler import YahooCrawler

#This Class is the mongoDB structure
class Post(mongoengine.Document):
    Platform = mongoengine.StringField(default="Reddit")
    PostID   = mongoengine.StringField(required=True)
    PostAuthor = mongoengine.StringField(required=False)
    PostText   = mongoengine.StringField(required=False)
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

        text = 'Welcome to the resurected u/TheYangGangBot!  ' \
               'Now running version 2.0.2.0!  ' \
               'Most of the bots bugs have been worked and fixed.  ' \
               'I have updated the bot to search the Yahoo Politcs RSS news feed looking for Democratic Primary News.  ' \
               'When the bot finds a post on Yahoo it is highly encourged for everyone to brigade the comment section' \
               'and try and convert some boomers!\n\n' \
               'This post is a megapost that gets updated through ' \
               'out the day whenever u/TheYangGangBot finds ' \
               'information on the internet and social media.' \
               ' When the bot finds information it will make a '\
               'comment in this post linking to the information.  ' \
               'Any suggestions or feed back please realy them to the bot creater u/Go_Big.  ' \


        # Catches rate limit error
        try:
            submission = self.reddit.subreddit('testingground4bots').submit(postTitle, selftext=text)
            #submission = self.reddit.subreddit('testingground4bots').submit(postTitle, selftext=text)
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
        print("RedditBot: Starting Reddit Comment Search")
        currentSubmission = self.reddit.submission(id=self.currentPostID)
        postSubmission = self.reddit.submission(id=postID)
        #Cycle through top level comments to find the right section to reply
        topComFound = False
        top_comment = None
        found = False
        for top_level_comment in currentSubmission.comments:
            if str(top_level_comment.body) == "Reddit" and top_level_comment.author.name == "TheYangGangBot":
                topComFound = True
                top_comment = top_level_comment
                print("RedditBot: Found Top Reddit Comment.")
                break

        if topComFound:
            for comment in top_comment.replies:
                print("RedditBot: Searching for Sub Comment.")
                # Check to make sure the comment is TheYangGangBot and the comment contains the subreddit
                commentSearchStr = 'R/' + str(postSubmission.subreddit).upper() + '.'
                if comment.author.name == "TheYangGangBot" and  commentSearchStr in comment.body.upper():
                    print("RedditBot: comment.body: %s comment.author: %s" % (comment.body, comment.author.name))
                    url = " https://np.reddit.com"+postSubmission.permalink
                    self.sendPrawCommand(comment.reply, url)
                    print("RedditBot: Making reddit comment %s" % url)
                    found = True
            if not found:
                print("RedditBot: Sub Comment not found.")
                replySub = "Posts from r/%s." % postSubmission.subreddit
                commentSub = self.sendPrawCommand(top_comment.reply, replySub)
                print("RedditBot: Making Sub Reddit Reply")
                url = " https://np.reddit.com" + postSubmission.permalink
                print("RedditBot: Making Reddit comment %s" % url)
                self.sendPrawCommand(commentSub.reply, url)
        else:
            print("RedditBot: Making Top comment for Reddit")
            replyPlatform = "Reddit"
            commentPlatform = self.sendPrawCommand(currentSubmission.reply, replyPlatform)
            replySub = "Posts from r/%s." % postSubmission.subreddit
            commentSub = self.sendPrawCommand(commentPlatform.reply, replySub)
            url = " https://np.reddit.com" + postSubmission.permalink
            print("RedditBot: Making Reddit comment %s" % url)
            self.sendPrawCommand(commentSub.reply, url)

            # reply = "Posts from r/%s" % postSubmission.subreddit
            # com = self.sendPrawCommand(top_level_comment.reply,reply)
            # url = " https://np.reddit.com" + postSubmission.permalink
            # print("RedditBot: Making reddit comment %s" % url)
            # self.sendPrawCommand(com.reply,url)
        #     found = True
        # if found:
        #     found = False
        #     break
        #
        # if not topComment:
        #     replyPlatform = "Reddit"
        #     commentPlatform = self.sendPrawCommand(currentSubmission.reply, replyPlatform)
        #     replySub = "Posts from r/%s" % postSubmission.subreddit
        #     commentSub = self.sendPrawCommand(commentPlatform.reply, replySub)
        #     url = " https://np.reddit.com" + postSubmission.permalink
        #     print("RedditBot: Making Reddit comment %s" % url)
        #     self.sendPrawCommand(commentSub.reply, url)

    def makeTwitterComment(self,postID,author,text):
        currentSubmission = self.reddit.submission(id=self.currentPostID)
        topComFound = False
        found = False
        top_comment = None
        for top_level_comment in currentSubmission.comments:
            if str(top_level_comment.body) == "Twitter" and top_level_comment.author.name == "TheYangGangBot":
                topComFound = True
                top_comment = top_level_comment
                print("RedditBot: Found Top Twitter Comment.")

        if topComFound:
            for comment in top_comment.replies:
                print("RedditBot: Searching for Twitter Author Comment.")
                if author.upper() in comment.body.upper() and comment.author.name == "TheYangGangBot":
                    commentText = str(text) + " " + postID
                    self.sendPrawCommand(comment.reply, commentText)
                    print("RedditBot: Making twitter comment under Author %s" % commentText)
                    found = True
            if not found:
                print("RedditBot: Twitter Author Comment not found.")
                replyAuthor = "Tweets from %s" % author
                commentAuthor = self.sendPrawCommand(top_comment.reply, replyAuthor)
                print("RedditBot: Creating Twitter Author Comment.")
                commentText = postID + " " + str(text)
                print("RedditBot: Making twitter comment %s" % commentText)
                self.sendPrawCommand(commentAuthor.reply, commentText)
        else:
            print("RedditBot: Creating Twitter Platform Comment.")
            replyPlatform = "Twitter"
            commentPlatform = self.sendPrawCommand(currentSubmission.reply, replyPlatform)
            replyAuthor = "Tweets from %s" % author
            commentAuthor = self.sendPrawCommand(commentPlatform.reply, replyAuthor)
            commentText = postID + " " + str(text)
            print("RedditBot: Making twitter comment %s" % commentText)
            self.sendPrawCommand(commentAuthor.reply, commentText)

        # if not found:
        #     reply = "Tweets from %s" % author
        #     com = self.sendPrawCommand(top_comment.reply,reply)
        #     commentText = postID + " " + str(text)
        #     print("RedditBot: Making twitter comment with new author %s" % commentText)
        #     self.sendPrawCommand(com.reply,commentText)
        #     found = True
        # else:
        #     found = False


    def makeYahooComment(self,url,headline):
        currentSubmission = self.reddit.submission(id=self.currentPostID)
        topComFound = False
        found = False
        top_comment = None
        for top_level_comment in currentSubmission.comments:
            if str(top_level_comment.body) == "Yahoo" and top_level_comment.author.name == "TheYangGangBot":
                topComFound = True
                top_comment = top_level_comment
                print("RedditBot: Found Top Yahoo Comment.")
                break

        if topComFound:
            commentText = str(headline) + "\n" + url
            self.sendPrawCommand(top_comment.reply, commentText)
            print("RedditBot: Making Yahoo comment %s" % commentText)
        else:
            print("RedditBot: Making Top Yahoo comment")
            replyPlatform = "Yahoo"
            commentPlatform = self.sendPrawCommand(currentSubmission.reply, replyPlatform)
            commentText = str(headline) + "\n" + url
            print("RedditBot: Making Yahoo comment %s" % commentText)
            self.sendPrawCommand(commentPlatform.reply, commentText)

    def searchDatabase(self):
        # searches all the posts in the database
        for post in Post.objects:
            if post.PostStatus == 0:
                # need to sleep for the post to register on reddit
                # otherwise I will get double postings.  Also helps with rate limit
                time.sleep(30)
                if str(post.Platform) == "Reddit":
                    print("RedditBot: Reddit Post Found")
                    self.makeSubRedditComment(post.PostID)
                    post.update(PostStatus = 1)
                if post.Platform == "Twitter":
                    print("RedditBot: Tweet Found")
                    self.makeTwitterComment(post.PostID,post.PostAuthor,post.PostText)
                    post.update(PostStatus=1)
                if post.Platform == "Yahoo":
                    print("RedditBot: News Article Found")
                    self.makeYahooComment(post.PostID,post.PostText)
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
        threadrc = Thread(target=rc.runCrawler)
        threadrc.start()
        tc = TwitterCrawler()
        threadtc = Thread(target=tc.runCrawler)
        threadtc.start()
        yc = YahooCrawler()
        threadyc = Thread(target=yc.runCrawler)
        threadyc.start()
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
                    #self.getActiveUsers()

                print("RedditBot: Sleeping 5 minutes")
                time.sleep(60)
            except Exception as e:
                print(e)
                # Shuts down our thread
                rc.running = False
                #tc.running = False
                yc.running = False


# unit test
if __name__ == "__main__":
    # from mongoengine import connect
    #
    # db = connect('yang_database')
    # db.drop_database('yang_database')
    rb =  RedditBot()
    #rb.currentPostID = 'cnfqqc'
    rb.run()

