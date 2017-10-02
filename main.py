import tweepy
import os
from collections import defaultdict

def box_contains(locations, lon, lat):
    """check if a box contains point (lon,lat)"""
    lon_inside = lon >= locations[0] and lon <= locations[2]
    lat_inside = lat >= locations[1] and lat <= locations[3]
    return lon_inside and lat_inside


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
        coordinate_pairs = status.place.bounding_box.coordinates[0]
        for coordinate_pair in coordinate_pairs:
            print(coordinate_pair)

        print(status.place.full_name)
        print(status.user.location)
        
        print(status.geo)
        for hashtag in status.entities['hashtags']:
            self.hashtag_frequency[hashtag['text']] += 1
        print(self.count)
        print(self.hashtag_frequency)

def main():
    auth = tweepy.OAuthHandler(os.environ['twitter_consumer_key'], os.environ['twitter_consumer_secret'])
    auth.set_access_token(os.environ['twitter_access_token_key'], os.environ['twitter_access_token_secret'])
    api = tweepy.API(auth)

    long1 = -88.36
    lat1 = 41.30
    long2 = -87.42
    lat2 = 42.48
    locations=[long1, lat1, long2, lat2]
    myStreamListener = MyStreamListener(locations)
    myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
    myStream.filter(locations=locations)
main()