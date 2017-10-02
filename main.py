import tweepy
import os
import datetime
import time
from collections import defaultdict
import operator
import pickle

def box_contains(box, lon, lat):
    """check if a box contains point (lon,lat)"""
    lon_inside = lon >= box[0] and lon <= box[2]
    lat_inside = lat >= box[1] and lat <= box[3]
    return lon_inside and lat_inside


class MyStreamListener(tweepy.StreamListener):

    def __init__(self, locations=None, *args, **kwargs):
        self.start_time = datetime.datetime.now()
        self.tweets = []
        self.coordinate_filtered_tweets = []
        self.count = 0
        self.placetag_count = 0
        self.geotag_count = 0
        self.placetags_outside_bounding_box = 0
        self.english_count = 0
        self.user_location_count = 0
        self.hashtag_frequency = defaultdict(int)
        self.box = locations
        tweepy.StreamListener.__init__(self, *args, **kwargs)

    def on_status(self, status):
        self.tweets.append(status)
        self.count += 1
        if self.box:
            coordinate_pairs = status.place.bounding_box.coordinates[0]
            pair_in_box = True
            for coordinate_pair in coordinate_pairs:
                pair_in_box = box_contains(self.box, *coordinate_pair)
                if not pair_in_box:
                    print('pair outside box')
                    print(coordinate_pair)
                    print(self.box)
                    print(status.place.full_name)
                    self.placetags_outside_bounding_box += 1
                    break
            if not pair_in_box:
                return
        self.coordinate_filtered_tweets.append(status)
        
        if status.geo:
            self.geotag_count += 1
        if status.place:
            self.placetag_count += 1
        for hashtag in status.entities['hashtags']:
            self.hashtag_frequency[hashtag['text']] += 1

        if status.user.lang == 'en':
            self.english_count += 1
        if status.user.location is not None:
            self.user_location_count += 1

    def output(self, part=1, keyword=None):
        print('STARTING OUTPUT')
        out_time = datetime.datetime.now()
        duration = out_time - self.start_time
        count = self.count
        filtered_count = len(self.coordinate_filtered_tweets)
        percent_place = self.placetag_count / filtered_count * 100    

        outlines = []
        outlines.append('PART {}'.format(part))
        outlines.append('Tweet collection started at {}'.format(self.start_time))
        outlines.append('This report was generated at {}'.format(out_time))

        if part == 1:
            outlines.append('Question 1')
            minutes = round(duration.total_seconds() / 60, 1)
            outlines.append('Over a {} minute period, {}* geographically tweets were collected, for a rate of {} geographically referenced tweets per minute'.format(
                minutes, count, count / minutes
            ))
            outlines.append('*this include placetagged tweets with coordinates outside the bounding box, which were filtered out for all other metrics')
            percent_geo = self.geotag_count / filtered_count * 100
            outlines.append('Question 2')
            outlines.append('{} percent of filtered tweets had geotags and {} percent of filtered tweets had placetags'.format(
                percent_geo, percent_place
            ))
            outlines.append('Question 3')
            outlines.append('{} total tweets actually had a placetag with coordinates outside the bounding box!'.format(
                self.placetags_outside_bounding_box
            ))
            outlines.append('Question 4')
            outlines.append('These tweets were filtered by checking if any coordinates associated with the placetag box were outside of the bounding box')
            

            outlines.append('Question 5')
            sorted_hashtags = sorted(self.hashtag_frequency.items(), key=operator.itemgetter(1))
            print(sorted_hashtags)
            if sorted_hashtags:
                outlines.append('The most popular hashtag in this report was {}, which appeared {} times'.format(*sorted_hashtags[0]))

            outlines.append('Question 6')
            english_percent = self.english_count / filtered_count * 100
            outlines.append('For this question, using the existing dataset, I decided to estimate what percent of Chicago Twitter users have English set as their primary language')
            outlines.append('{} percent of tweets came from users with English set as their primary language'.format(
                english_percent
            ))

            outlines.append('Question 7')
            outlines.append('Key Code:')
            outlines.append("""
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
                myStream.filter(locations=locations)""")
            outlines.append('Full code at https://github.com/nickmvincent/twitter_explore')
        elif part == 2:
            outlines.append('The keyword was {}'.format(keyword))
            outlines.append('Question 1')
            outlines.append('{} percent of tweets for the keyword {} had place tags'.format(
                percent_place, keyword
            ))
            outlines.append('Question 2')
            percent_user_location = self.user_location_count / filtered_count * 100
            outlines.append('{} percent of tweets for the keyword {} had non-null user location fields'.format(
                percent_user_location, keyword
            ))
            for tweet in self.coordinate_filtered_tweets[:50]:
                if tweet.user.location:
                    outlines.append(tweet.user.location)
        

        filename = 'part{}'.format(part)
        if keyword:
            filename += '_keyword_{}'.format(keyword)
        datasetname = filename + '_dataset.p'
        filename += '_output.txt'
        print(outlines)
        with open(filename, 'w') as outfile:
            outstr = '\n'.join(outlines)
            outfile.write(outstr)
        pickle.dump(self.coordinate_filtered_tweets, open(datasetname, "wb" ) )

        

            
DURATION = 600
def main():
    auth = tweepy.OAuthHandler(os.environ['twitter_consumer_key'], os.environ['twitter_consumer_secret'])
    auth.set_access_token(os.environ['twitter_access_token_key'], os.environ['twitter_access_token_secret'])
    api = tweepy.API(auth)

    long1 = -88.36
    lat1 = 41.30
    long2 = -87.42
    lat2 = 42.48
    locations=[long1, lat1, long2, lat2]
    stream_listener = MyStreamListener(locations)
    my_stream = tweepy.Stream(auth = api.auth, listener=stream_listener)
    my_stream.filter(locations=locations, async=True)
    start = time.time()
    while True:
        time_elapsed = time.time() - start
        if time_elapsed > DURATION:
            my_stream.disconnect()
            stream_listener.output(1)
            break

    keywords = ['NFL', 'Trump', 'Hurricane']
    for keyword in keywords:
        stream_listener = MyStreamListener()
        my_stream = tweepy.Stream(auth = api.auth, listener=stream_listener)
        my_stream.filter(track=[keyword], async=True)
        start = time.time()
        while True:
            time_elapsed = time.time() - start
            if time_elapsed > DURATION:
                my_stream.disconnect()
                stream_listener.output(2, keyword)
                break


main()