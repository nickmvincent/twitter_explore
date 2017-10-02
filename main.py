import tweepy
import os
from collections import defaultdict
#override tweepy.StreamListener to add logic to on_status
# {
#  'contributors': None, 
#  'truncated': False, 
#  'text': 'My Top Followers in 2010: @tkang1 @serin23 @uhrunland @aliassculptor @kor0307 @yunki62. Find yours @ http://mytopfollowersin2010.com',
#  'in_reply_to_status_id': None,
#  'id': 21041793667694593,
#  '_api': <tweepy.api.api object="" at="" 0x6bebc50="">,
#  'author': <tweepy.models.user object="" at="" 0x6c16610="">,
#  'retweeted': False,
#  'coordinates': None,
#  'source': 'My Top Followers in 2010',
#  'in_reply_to_screen_name': None,
#  'id_str': '21041793667694593',
#  'retweet_count': 0,
#  'in_reply_to_user_id': None,
#  'favorited': False,
#  'retweeted_status': <tweepy.models.status object="" at="" 0xb2b5190="">,
#  'source_url': 'http://mytopfollowersin2010.com', 
#  'user': <tweepy.models.user object="" at="" 0x6c16610="">,
#  'geo': None, 
#  'in_reply_to_user_id_str': None, 
#  'created_at': datetime.datetime(2011, 1, 1, 3, 15, 29), 
#  'in_reply_to_status_id_str': None, 
#  'place': None
# }

class MyStreamListener(tweepy.StreamListener):

    def __init__(self):
        self.tweets = []
        self.placetag_count = 0
        self.geotag_count = 0
        self.placetags_outside_bounding_box = 0
        self.count = 0
        self.hashtag_frequency = defaultdict(int)
        tweepy.StreamListener.__init__(self)

    def on_status(self, status):
        self.tweets.append(status)
        self.count += 1
        print(status.place)
        print(status.geo)
        for hashtag in status.entities['hashtags']:
            self.hashtag_frequency[hashtag['text']] += 1
        print(self.count)
        print(self.hashtag_frequency)

def main():
    # api_kwargs = {
    #     'consumer_key': os.environ['twitter_consumer_key'],
    #     'consumer_secret': os.environ['twitter_consumer_secret'],
    #     'access_token_key': os.environ['twitter_access_token_key'],
    #     'access_token_secret': os.environ['twitter_access_token_secret']
    # }
    auth = tweepy.OAuthHandler(os.environ['twitter_consumer_key'], os.environ['twitter_consumer_secret'])
    auth.set_access_token(os.environ['twitter_access_token_key'], os.environ['twitter_access_token_secret'])
    api = tweepy.API(auth)

    long1 = -88.36
    lat1 = 41.30
    long2 = -87.42
    lat2 = 42.48
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
    myStream.filter(locations=[long1, lat1, long2, lat2])
main()