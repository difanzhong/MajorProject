import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import db
import pre_processing

consumer_key = '5kDnOi1br8qk6ySNLmu05cpUr'
consumer_secret = 'EYLu9iisDpGzOYsbdqvBgx5nvjSg6lcERY7Fq1r2lSy9YZX53i'
access_token = '863347247836086272-dKCP7OHqeaRohrESNfydqTNWWeRTzmj'
access_secret = 'hkA2KdVVAEHOsMzAORzFIH4q9voIgiL9XC6q24k1Ewh4W'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

class listener(StreamListener):

    def __init__(self):
        self._count = 0
        self._db = db.DBConnect()
        self._textmining = pre_processing.PreProcessing()
        self._db.connect()

    def on_data(self, data):
        #print(data)

        obj = json.loads(data)

        time_arr = obj['created_at'].split(' ')
        time_arr.pop(0)
        time_arr.pop(3)
        new_time = " ".join(time_arr)


        tweet = obj['text']
        t_tweet = self._textmining.preprocess(tweet)

        print(t_tweet)
        print(new_time)

        if obj['coordinates'] is not None:
            #suburb_id = db.getSuburbId()

            lon = obj['coordinates']['coordinates'][0]
            lat = obj['coordinates']['coordinates'][1]
            id = self._db.getSuburbId(lon, lat)
            if id is not None:
                self._db.insert_tweet(new_time, tweet, t_tweet.__str__(), id[0])

        elif obj['place'] is not None:
            if obj['place']['bounding_box'] is not None:

                corner_points = obj['place']['bounding_box']['coordinates'][0]
                bottom_left_point = corner_points[0]
                top_right_point = corner_points[2]
                centre_point_lon = (bottom_left_point[0] + top_right_point[0]) / 2
                centre_point_lat = (bottom_left_point[1] + top_right_point[1]) / 2
                print(centre_point_lon)
                print(centre_point_lat)
                id = self._db.getSuburbId(centre_point_lon, centre_point_lat)
                if id is not None:
                    self._db.insert_tweet(new_time, tweet, t_tweet.__str__(), id[0])

        self._count+=1
        if self._count % 10 == 0:
            print(self._count)
        return True
    def on_error(self,status):
        print(status)


api = tweepy.API(auth)

twitterStream = Stream(auth, listener())
twitterStream.filter(locations=[113.338953078, -43.6345972634, 153.569469029, -10.6681857235])
#
#dbs = db.DBConnect()
#dbs.connect()
#dbs.insert_tweet("May 19 11:50:24 2017","What a ni'ght \u270c\ufe0f\u270c\ufe0f\u270c\ufe0f ht'tps:\/\/t.co\/mNmYbqHoT4","dfs,sd","2344")
#

#pp = pre_processing.PreProcessing()
#print(pp.preprocess("RT @marcobonzanini: just an example! 你好啊 :D http://example.com #NLP"))