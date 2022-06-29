import os
import time
import tweepy

if os.path.exists("config.py"):
    from config import CONFIG
    consumer_key = CONFIG["CONSUMER_KEY"]
    consumer_secret = CONFIG["CONSUMER_SECRET"]
    access_token = CONFIG["ACCESS_TOKEN"]
    access_token_secret = CONFIG["ACCESS_SECRET"]
else:    
    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_SECRET"]    

def tweet(text, contents):
    global consumer_key
    global consumer_secret
    global access_token
    global access_token_secret

    client = tweepy.Client(
        consumer_key = consumer_key,
        consumer_secret = consumer_secret,
        access_token = access_token,
        access_token_secret = access_token_secret
    )
    data, text, _, _ = client.create_tweet(text=text)
    id = data["id"]
    for i, content in enumerate(contents):
        client.create_tweet(text=content, in_reply_to_tweet_id=id)
        time.sleep(2)
