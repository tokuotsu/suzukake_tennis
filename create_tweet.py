import os
import time
import datetime
import tweepy
import numpy as np
from property import DISPLAY_NAME

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

def num2youbi(num):
    if type(num) == str:
        num = int(num)
    youbi = ["日", "月", "火", "水", "木", "金", "土"]
    return youbi[num]

def getJST():
    # return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
    return datetime.datetime.now()

def make_body_day(search_date, now_date, dictionary, type_season):
    now_date = now_date.strftime("%m/%d %H:%M:%S")
    search_date = search_date.strftime("%m/%d") + f"（{num2youbi(search_date.strftime('%w'))}）"
    body = f"{search_date} 予約状況\n{'-'*12} | A | B | C |\n"
    for key, value in dictionary.items():
        value = np.array(value)
        value = np.where(value==0, "×", "○")
        body += f"{DISPLAY_NAME[type_season][key]} | {' | '.join(value)} |\n"
    # body += f"\n{now_date} 現在"
    return body

def make_body_week(weekly_dict, is_fomer=True):
    now_date = getJST().strftime("%m/%d %H:%M:%S")  
    body = f"1週間の予約状況\n数字は残り面数\n{'-'*12} | A | B | C \n"
    for i, (key, value) in enumerate(weekly_dict.items()):
        if is_fomer:
            if i > 6:
                continue
        else:
            if i < 7:
                continue        
        value = np.array(value)
        body += f"{key} | {' | '.join(list(map(str, map(int, value.sum(axis=0)))))} |\n"
    body += f"\n{now_date} 現在"
    print(body)
    return body
    # pass

if __name__=="__main__":
    a = getJST()
    print(a)