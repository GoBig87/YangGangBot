import praw
from datetime import datetime
import mongoengine
import time

#This Class is the mongoDB structure
class Post(mongoengine.Document):
    Platform = mongoengine.StringField(default="Reddit")
    PostID   = mongoengine.StringField(required=True)
    PostText = mongoengine.StringField(required=False)
    PostStatus = mongoengine.IntField(default=0)

class RedditCrawler():
    def __init__(self):
        #From mongoengine, connects to DB
        self.running = True
        mongoengine.connect('yang_database')

        self.subreddits = ["asklibertarians", "classical_liberals",
                           "goldandblack", "libertarian", "libertariandebates",
                           "libertarianmeme", "libertarianpartyusa", "shitstatistssay",
                           "WorldNews","News","WorldPolitics","WorldEvents","Business",
                           "Economics","Environment","Energy","Law","Education",
                           "Government","History","PoliticsPDFs","Wikileaks","SOPA",
                           "NewsPorn","WorldNews2","RepublicofPolitics",
                           "LGBTNews","Politics2","Economics2","Environment2","Politics",
                           "USPolitics","AmericanPolitics","AmericanGovernment",
                           "Libertarian","Anarchism","Socialism","Progressive","Conservative",
                           "AmericanPirateParty","Democrats","Liberal","New_Right",
                           "Republican","Egalitarian","DemocraticSocialism","LibertarianLeft",
                           "Liberal","New_Right","Republican","Egalitarian","DemocraticSocialism",
                           "LibertarianLeft","Liberty","AnarchoCapitalism","AlltheLeft",
                           "neoprogs","Tea_Party","Voluntarism","Labor","BlackFlag","GreenParty",
                           "Democracy","IWW","PirateParty","Marxism","Objectivism",
                           "LibertarianSocialism","PeoplesParty","Capitalism","Anarchist",
                           "Feminisms","Republicans","Egalitarianism","AnarchaFeminism",
                           "Communist","SocialDemocracy","PostLeftAnarchism","RadicalFeminism",
                           "AnarchoPacifism","Conservatives","Republicanism","FreeThought",
                           "FoodforThought","StateoftheUnion","ModeratePolitics",
                           "PoliticalDiscussion","Equality","CulturalStudies","PoliticalHumor",
                           "PropagandaPosters","SocialScience","PoliticalPhilosophy","Media",
                           "Culture","Racism","Corruption","Activism","Revolution",
                           "NoamChomsky","Propaganda","PeterSchiff","VotingTheory",
                           "ReligionInAmerica","Debate","FoodSovereignty",
                           "LGBT","MensRights","Collapse","OperationGrabAss",
                           "Permaculture","Food2","Anonymous","Censorship","Feminism","Sunlight",
                           "Privacy","OccupyWallStreet","ResilientCommunities","ChangeNow",
                           "PrisonReform","TSA","ElectionReform","TroubledTeens",
                           "StrikeAction","YouthRights","HumanRights","CPAR",
                           "BlackOps","Intelligence","MidEastPeace","EndlessWar",
                           "FirstAmendment","Union","Antiwar","War","Peace","askaconservative",
                            "conservative", "conservativelounge", "conservatives",
                           "jordanpeterson", "louderwithcrowder",
                           "paleoconservative", "republican", "the_donald",
                           "thenewright", "threearrows", "tuesday", "walkaway",
                           "againsthatesubreddits", "anarchism", "anarchocommunism", "anarchy101", "antiwork",
                           "bannedfromthe_donald", "beto2020", "breadtube",
                           "centerleftpolitics", "chapotraphouse2", "chapotraphouse", "chomsky", "communism101",
                           "communism", "completeanarchy", "debateanarchism",
                           "debatecommunism", "demsocialists", "enoughlibertarianspam",
                           "enoughtrumpspam", "esist", "fuckthealtright",
                           "greenparty", "impeach_trump", "keep_track", "latestagecapitalism", "leftwithoutedge",
                           "liberal", "marchagainsttrump", "neoliberal",
                           "ourpresident", "political_revolution", "politicalhumor", "progressive", "russialago",
                           "sandersforpresident", "selfawarewolves",
                           "shitliberalssay", "shitthe_donaldSays", "socialism", "socialism_101", "the_mueller",
                           "topmindsofreddit", "voteblue", "wayofthebern"]

        self.reddit = praw.Reddit(client_id="soXdD-RwcsgTPA",
                             client_secret='BWLl9zDrpDrDDFc-OUqKYd-AD84',
                             user_agent='The Yang Gang Bot',
                             username='TheYangGangBot',
                             password= 'securethebag')

    def getPosts(self):
        for subreddit in self.subreddits:
            print("RedditCrawler: %s" % subreddit)
            time.sleep(5)
            submissions = self.reddit.subreddit(subreddit).new(limit=1000)
            for submission in submissions:
                ts = submission.created - 7*3600 # GMT time is 7 hours ahead, subtract 7 hours to get PST
                postDate = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                currentDate =datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')
                if postDate == currentDate:
                   currentSubmission = submission.title.upper()
                   # Keep this like \sYANG.  The space weeds out things like Pyongyang
                   if " YANG" in submission.title.upper() and "CINDY" not in submission.title.upper():
                       if Post.objects(PostID=submission.id).count():
                            print("RedditCrawler: Print Post already in DB")
                       else:
                           print("RedditCrawler: %s" % currentSubmission)
                           post = Post(PostID=submission.id)
                           post.save()
                else:
                    #Posts are no longer from today
                    break
                if not self.running:
                    break
            if not self.running:
                break

    def runCrawler(self):
        while self.running:
            try:
                self.getPosts()
                #Sleep 10 minutes between crawls
                print("RedditCrawler: Sleeping 10 minute")
                time.sleep(600)
            except:
                pass

# unit test
if __name__ == "__main__":
    rc =  RedditCrawler()
    rc.run()