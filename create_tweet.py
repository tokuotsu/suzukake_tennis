import os
import time
import pickle
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
        data, text, _, _, = client.create_tweet(text=content, in_reply_to_tweet_id=id)
        # ツリーにする
        id = data["id"]
        time.sleep(2)
    print("tweeted")

def num2youbi(num):
    if type(num) == str:
        num = int(num)
    youbi = ["日", "月", "火", "水", "木", "金", "土"]
    return youbi[num]

def getJST():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
    # return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))+ datetime.timedelta(hours=4)
    # return datetime.datetime.now()

# ツリーにつなげる詳細ツイートの作成
def make_body_day(search_date, now_date, dictionary, type_season):
    now_date = now_date.strftime("%m/%d %H:%M:%S")
    search_date = search_date.strftime("%m/%d") + f"（{num2youbi(search_date.strftime('%w'))}）"
    body = f"{search_date} 空き状況\n{'-'*16} | A | B | C | \n"
    for key, value in dictionary.items():
        value = np.array(value)
        value = np.where(value%100==0, "×", "○")
        # 
        # value = np.where(value%100==0, "×", value)
        # value = np.where(value==1, "○", value)
        # value = np.where(value==101, "(○)", value)
        body += f"{DISPLAY_NAME[type_season][key]} | {' | '.join(value)} | \n"
    body += f"\n({now_date})"
    return body

# 1週間分の空きコート数の作成
def make_body_week(weekly_dict, is_difference, is_former):
    now_date = getJST().strftime("%m/%d %H:%M")  
    if is_difference:
        body = f"【更新】\n{now_date}現在の予約状況\n{'='*7} | A | B | C | \n"
    else:
        body = f"【定期】\n{now_date}現在の予約状況\n{'='*7} | A | B | C | \n"

    for i, (key, value) in enumerate(weekly_dict.items()):       
        value = np.array(value)
        # 縦方向に足し算
        sum_list = list(map(int, value.sum(axis=0)))
        # 変更があったものについては、*をつける
        for i, sum_li in enumerate(sum_list):
            if sum_li%100 >= 10:
                sum_list[i] = str(sum_li%10) + "*"
            else:
                sum_list[i] = str(sum_li%100)
            if sum_li >= 100:
                sum_list[i] = f"({sum_list[i]})"
        body += f"{key} | {' | '.join(sum_list)} | \n"
    # body += f"\n{now_date} 現在"
    if getJST().hour < 17 and (not is_former):
        return body
    else:
        if is_difference:
            body += "\n※*は変更分"
        else:
            body += "\n※数字は残り面数"
        print(body)
        return body

# 変更の有無による処理の変更
def detect_difference(weekly_dict, weekly_dict_mask, zenkai_dict, bodies_list, is_former):
    flag = True
    for key, value in weekly_dict.items():
        # 新しい日付のもの
        if key not in zenkai_dict.keys():
            flag = False
            if is_former:
                with open("./zenkai_former.txt", "wb") as f:
                    pickle.dump(weekly_dict, f)
            else:
                with open("./zenkai_latter.txt", "wb") as f:
                    pickle.dump(weekly_dict, f)
            # exit()
            return "end", "end"
            # return weekly_dict, bodies_list
        zenkai_value = zenkai_dict[key]
        if value!=zenkai_value:
            flag = False
            break
    # 変化が無かった場合
    if flag:
        print(f"{getJST()}:\nThere is no difference")
        return "end", "end"
        # exit()
    else:
        new_bodies_list = []
        for (key, value), body in zip(weekly_dict.items(), bodies_list):
            zenkai_value = np.array(zenkai_dict[key])
            value = np.array(value)
            tflist = value==zenkai_value
            new_value = np.where(tflist, value, value+10)
            weekly_dict_mask[key] = new_value

            body_list = [bod.split(' | ') for bod in body.split("\n")]
            for i, body in enumerate(body_list):
                for j, bo in enumerate(body):
                    if bo == "×" or bo == "○":
                        if not tflist[i-2][j-1]:
                            body_list[i][j]+="*"
            new_bodies_list.append("\n".join([" | ".join(body) for body in body_list]))
        if is_former:
            with open("./zenkai_former.txt", "wb") as f:
                pickle.dump(weekly_dict, f)
        else:
            with open("./zenkai_latter.txt", "wb") as f:
                pickle.dump(weekly_dict, f)

    return weekly_dict_mask, new_bodies_list

if __name__=="__main__":
    a = getJST()
    print(a)
