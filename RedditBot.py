import praw

class RedditBot():
    def __init__(self):
        self.reddit = praw.Reddit(client_id="INSERT ID HERE",
                             client_secret='INSERT CLIENT KEY HERE',
                             user_agent='The Yang Gang Bot',
                             username='TheYangGangBot',
                             password= 'securethebag')
    #TODO
    def makePost(self):
        pass

    # TODO
    def addComment(self):
        pass