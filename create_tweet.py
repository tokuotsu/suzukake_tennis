import os
import time
import pickle
import datetime
import tweepy
import numpy as np
from property import DISPLAY_NAME, DISPLAY_NAME_2

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
        # time.sleep(2)
    print("tweeted")


def num2youbi(num):
    if type(num) == str:
        num = int(num)
    youbi = ["日", "月", "火", "水", "木", "金", "土"]
    return youbi[num]



def getJST():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
    # デバッグ用、日付を変更できる
    # return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))+ datetime.timedelta(hours=5)
    # return datetime.datetime.now()


# ツリーにつなげる詳細ツイートの作成
def make_body_day(search_date, now_date, dictionary, type_season):
    now_date = now_date.strftime("%m/%d %H:%M:%S")
    search_date_str1 = search_date.strftime("%m/%d") + f"({num2youbi(search_date.strftime('%w'))})"

    body = f"{search_date_str1}\n{'='*7} |  A  |  B  |  C|\n"
    for key, value in dictionary.items():
        # value = np.array(value)
        # 100で割った余りが0なら×、それ以外は全て○
        # value = np.where(value%100==0, "×", "○")
        # body += f"{DISPLAY_NAME[type_season][key]} | {' | '.join(value)} | \n"
        
        # 全表示
        value = str(value).replace("[", "").replace("]", "").replace("101", "(○)").replace("100", "(×)").replace("1", " ○ ").replace("0", " × ")
        value = value.split(", ")
        if key in DISPLAY_NAME_2[type_season].keys():
           body += f"{DISPLAY_NAME_2[type_season][key]} | {' | '.join(value)} |\n"
        else:
            body += f"{key} | {' | '.join(value)} |\n"
    body += f"\n({now_date})"
    body += f"\n#suzukake_{search_date.strftime('%Y%m%d')}"
    body_display = body.replace("|", "")
    return body, body_display


def make_body_week2(weekly_dict, is_difference):
    print("make_body_week2 started...")
    now_date = getJST().strftime("%m/%d %H:%M")  
    if is_difference:
        body = f"【更新 1/2】\n{now_date}現在の残り面数\n\n{'='*8} | A |  B  | C|\n"
    else:
        body = f"【定期 1/2】\n{now_date}現在の残り面数\n\n{'='*8} | A |  B  | C|\n"
    body1 = body
    body2 = body.replace(" 1/2】", " 2/2】").replace(f"{now_date}現在の残り面数\n", "")
    num_list = ["⓪", "①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩", "⑪", "⑫", "⑬", "⑭"]
    for i, (key, value) in enumerate(weekly_dict.items()):
        is_former = i <= 7
        if getJST().hour >= 17 and i==0:
            continue       
        value = np.array(value)
        # 縦方向に足し算
        sum_list = list(map(int, value.sum(axis=0)))
        # 変更があったものについては、*をつける
        for j, sum_li in enumerate(sum_list):
            # 100で割った余りが10以上なら変更がある
            if sum_li%100 >= 10:
                sum_list[j] = str(sum_li%10) + "*"
            else:
                sum_list[j] = str(sum_li%100)
            # 101なら何らかの理由で予約できない日、400以上なら土日祝教員用のためカッコをつける(最低4つあるため)
            if sum_li >= 400:
                sum_list[j] = f"({sum_list[j]})"
            elif max(sum_li - 101, -1) % 10 == 0:
                sum_list[j] = f"({sum_list[j]})"
            else:
                # if j == 1: # 真ん中の列
                sum_list[j] = f" {sum_list[j]} "
        if is_former:
            body1 += f"{num_list[i]}{key}  {'|'.join(sum_list)}\n"
        else:
            body2 += f"{num_list[i]}{key}  {'|'.join(sum_list)}\n"

    if is_difference:
        body2 += "\n※* は変更分"
    else:
        if not is_former:
            body2 += "\n※詳細はツリーへ"

    body1 = body1.replace("|", " ")
    body2 = body2.replace("|", " ")
    print(body1)
    print(body2)
    return body1, body2


# 変更の有無による処理の変更
def detect_difference2(weekly_dict, weekly_dict_mask, zenkai_dict, bodies_list):
    flag = True
    for key, value in weekly_dict.items():
        # 新しい日付の場合、ツイートせず、データ保存のみ
        if key not in zenkai_dict.keys():
            with open("./zenkai.pkl", "wb") as f:
                pickle.dump(weekly_dict, f)
            print(f"New date, data saved only")
            return "end", "end"
            # return weekly_dict, bodies_list
        zenkai_value = zenkai_dict[key]
        if value!=zenkai_value:
            flag = False
            # break
    # 変化が無かった場合
    if flag:
        print(f"There is no difference")
        return "end", "end"
    else:
        new_bodies_list = []
        for (key, value), body in zip(weekly_dict.items(), bodies_list):
            flag = False
            zenkai_value = np.array(zenkai_dict[key])
            value = np.array(value)
            tflist = value==zenkai_value
            # 変更があった場合、10を足す
            new_value = np.where(tflist, value, value+10)
            weekly_dict_mask[key] = new_value
            # 変更があった場合、文字列の状態からばらして、*を追加
            body_list = [bod.split(' | ') for bod in body.split("\n")]
            for i, body in enumerate(body_list):
                for j, bo in enumerate(body):
                    if "×" in bo or "○" in bo:
                        if not tflist[i-2][j-1]:
                            body_list[i][j] = body_list[i][j].replace("○ ", "○*").replace("× ", "×*").replace("○)", "○*)").replace("×)", "×*)")
                            flag = True
            if flag:
                # 再構成
                new_bodies_list.append("\n".join([" | ".join(body) for body in body_list]))
            # else:
            #     del weekly_dict_mask[key]

        new_bodies_list = [body.replace("|", "") for body in new_bodies_list]
        # 前回のデータを更新
        with open("./zenkai.pkl", "wb") as f:
            pickle.dump(weekly_dict, f)

    return weekly_dict_mask, new_bodies_list

if __name__=="__main__":
    a = getJST()
    print(a)