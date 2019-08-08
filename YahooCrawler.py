from datetime import date
import mongoengine
import time
import feedparser

#This Class is the mongoDB structure
class Post(mongoengine.Document):
    Platform = mongoengine.StringField(default="Yahoo")
    PostID   = mongoengine.StringField(required=True)
    PostText = mongoengine.StringField(required=False)
    PostStatus = mongoengine.IntField(default=0)

class YahooCrawler():
    def __init__(self):
        #From mongoengine, connects to DB
        self.running = True
        mongoengine.connect('yang_database')
        self.url = 'http://news.yahoo.com/politics/rss/'

        self.key_words = ['Democratic candidates',
                          'Yang',
                          'DNC',
                          ' Election',
                          'Presidential',
                          'Primary',
                          'Democratic debate',
                          'Democratic Primary'

        ]

    def getArticles(self):
        info = feedparser.parse(self.url)
        today = date.today()
        for entry in info['entries']:
            for key in self.key_words:
                if key.upper() in entry['title'].upper():
                    post_date = str(entry['published_parsed'][0]) + '-' + \
                                str(entry['published_parsed'][1]) + '-' + \
                                str(entry['published_parsed'][2])
                    # if today == post_date:
                    temp = int(str(today).split('-')[2]) - int(str(post_date).split('-')[2])
                    print('Yahoo date value: %s' % temp)
                    if temp < 5:
                        if Post.objects(PostID=entry.link).count():
                            print("YahooCrawler: News Article already in DB")
                        else:
                            print("YahooCrawler: %s" % entry['title'])
                            post = Post(PostID=entry.link,PostText=entry['title'])
                            post.save()
                    else:
                        print("YahooCrawler: %s is from %s.  Today is %s." % (entry['title'],post_date,today))
        pass  # here for debuggin and break point stoppage

    def runCrawler(self):
        while self.running:
            try:
                print('YahooCrawler: Starting yahoo crawler')
                self.getArticles()
                #Sleep 10 minutes between crawls
                print("YahooCrawler: Sleeping 10 minute")
                time.sleep(600)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    yc = YahooCrawler()
    yc.getArticles()