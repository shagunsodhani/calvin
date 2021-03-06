from ConfigParser import ConfigParser
from PIL import Image
from StringIO import StringIO
import os

from time import time, sleep
from dateutil.parser import parse

import tweepy
import requests

import mysql
from constants import *

def process_pipeline(data, fns):
    return reduce(lambda a, x: map(x, a),
        fns,
        data)

def get_tweets(auth, screen_name, since_id = -1):
    
    """
        Method to download tweets from a user. Note that the Twitter API allows only 3200 most recent tweets to be downloaded.

        **Parameters**
            screen_name : Screen name of the user whose tweets are to be downloaded.
            since_id : Tweets collected will be of id greater than this id. This parameter allows tweets to be collected in an incremental fashion.
                Default value is -1 in which case all tweets are downloaded.
    """
    api = tweepy.API(auth)
    if(since_id==-1):
        for tweet in tweepy.Cursor(api.user_timeline, screen_name = screen_name).items():
            yield tweet._json
    else:
        for tweet in tweepy.Cursor(api.user_timeline, screen_name = screen_name, since_id = since_id).items():
            yield tweet._json


def parse_tweet(tweet):

    """
        Method to parse the tweet to obtain the status and the media files. It returns two dicts - one dict for tweet data and other for media data. Each key for the dict is the corresponding column name in database.

        **Parameters**
            tweet : Tweet object to be parsed.
    """
    data_list = []
    data = {}
    data[TEXT] = tweet[TEXT]
    data[ID] = tweet[ID]
    data[CREATED_AT] = parse(tweet[CREATED_AT]).strftime("%Y-%m-%d %H:%M:%S")
    data_list.append(data)

    media_list = []
    
    if MEDIA in tweet[ENTITIES]:
        for entity in tweet[ENTITIES][MEDIA]:
            media = {}
            media[TWEET_ID] = data[ID]
            media[URL] = entity[MEDIA_URL_HTTPS]
            media[PATH] = "images/"+str(int(time()*1000))+"."+media[URL].split(".")[-1]
            response = requests.get(media[URL]+":large", stream=True)
            if(response.status_code == requests.codes.ok):  
                image = Image.open(StringIO(response.content))
                path = os.path.dirname(os.path.abspath('__file__')) + "/" +  media[PATH]
                image.save(path)
                del response
            else:
                error_message = "ERROR \nInvalid URL\n" + str(media[URL]) + "\n\n\n"  
            media_list.append(media)

    payload = {}
    payload[TWEET] = data_list
    payload[MEDIA] = media_list

    return payload

def insert_tweet(payload, cursor, conn, f):

    """
        Method to insert the payload into mysql instance. 

        **Parameters**
            payload: dict containing tweet_list and media_list. tweet_list is the list of tweet objects to be dumped into the database and media_list is the list of media items belonging to the tweet that is to be dumped.
            cursor: cursor object
            conn: connection object
            f: file object to which errors are logged.
    """
    for (table, data) in payload.items():
        column_string = "("
        value_string = "("
        if data:
            for (key, value) in data[0].items():
                column_string+=key+","
                try:
                    value_string+="\""+str(str(value).replace('"','\\"').replace("'","\\'"))+"\""+","
                except UnicodeEncodeError as e:
                    error_message = "ERROR \n" + str(e) + "\n" + str(data) + "\n\n\n" 
                    f.write(error_message)
                    value_string+=DEFAULT_VALUE+","
            column_string = column_string[:-1] + ")"
            value_string = value_string[:-1] + "),"
            
            if data[1:]:
                for d in data[1:]:
                    value_string += "("
                    for (key, value) in d.items():
                        value_string+="\""+str(str(value).replace('"','\\"').replace("'","\\'"))+"\""+","
                    value_string = value_string[:-1] + "),"
            value_string = value_string[:-1]

            sql = "INSERT into "+table+" "+column_string+ " VALUE "+value_string
            mysql.write(sql, conn, cursor)       
   

def run():
    """
        Method to run the entire pipeline.
    """
    
    CONFIG_PATH = "config/config.cfg"

    config=ConfigParser()
    config.read(CONFIG_PATH)
    host=config.get(DATABASE, HOST)
    user=config.get(DATABASE, USER)
    password=config.get(DATABASE, PASSWORD)
    db=config.get(DATABASE, DB)
    charset=config.get(DATABASE,CHARSET)
    use_unicode=config.get(DATABASE, USE_UNICODE)
    consumer_key=config.get(TWITTER, CONSUMER_KEY)
    consumer_secret=config.get(TWITTER, CONSUMER_SECRET)
    access_token=config.get(TWITTER, ACCESS_TOKEN)
    access_token_secret=config.get(TWITTER, ACCESS_TOKEN_SECRET)
    log_error_file=config.get(LOG, ERROR_FILE)

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    conn = mysql.connect(host, user, password, db, charset, use_unicode)
    cursor=conn.cursor()

    f = open(log_error_file,'a')

    flag = True
    while flag:
        try:
            sql = "SELECT max(id) FROM tweet"
            result = mysql.read(sql, cursor)
            if result[0][0]:
                since_id = int(result[0][0])
            else:
                since_id = -1
            print since_id
            for payload in process_pipeline(get_tweets(auth = auth, screen_name = "Calvinn_Hobbes", since_id = since_id), [parse_tweet]):
                insert_tweet(payload, cursor, conn, f)
            flag = False
        except tweepy.error.TweepError as e:
            error_message = "ERROR \n" + str(e) + "\nsleeping for 15 minutes\n\n\n"
            f.write(error_message)
            sleep(15*60)
    f.close()

if __name__ == '__main__':

    run()