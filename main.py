#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import copy
import pickle
import datetime
import numpy as np
import pandas as pd
from collections import defaultdict
from property import DISPLAY_NAME
from create_tweet import *

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

is_debug = True

# ローカルでは必要
if is_debug:
    import chromedriver_binary

if os.path.exists("config.py"):
    from config import CONFIG
    STUDENT_ID = CONFIG["STUDENT_ID"]
    PASSWORD = CONFIG["PASSWORD"]
    MATRIX = CONFIG["MATRIX"]
else:    
    STUDENT_ID = os.environ["STUDENT_ID"]
    PASSWORD = os.environ["PASSWORD"]
    MATRIX = os.environ["MATRIX"]
    outers = MATRIX.split("|")
    MATRIX = [outer.split(",") for outer in outers]

def scraping(is_former=True, is_difference=False):
    global STUDENT_ID
    global PASSWORD
    global MATRIX
    url = "https://portal.nap.gsic.titech.ac.jp/GetAccess/Login?Template=userpass_key&AUTHMETHOD=UserPassword"
    options = Options()
    # ブラウザ表示の有無
    if not is_debug:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # ログイン
    time.sleep(1)
    id = driver.find_element(By.NAME, "usr_name")
    id.send_keys(STUDENT_ID)
    password = driver.find_element(By.NAME, "usr_password")
    password.send_keys(PASSWORD)
    button = driver.find_element(By.NAME, "OK")
    button.click()
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
    
    # マトリックス認証
    coordinate1 = driver.find_element(By.XPATH, "//*[@id='authentication']/tbody/tr[4]/th[1]").text
    coordinate2 = driver.find_element(By.XPATH, "//*[@id='authentication']/tbody/tr[5]/th[1]").text
    coordinate3 = driver.find_element(By.XPATH, "//*[@id='authentication']/tbody/tr[6]/th[1]").text
    alpha = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    loc1 = [alpha.index(coordinate1[1]), int(coordinate1[3])-1]
    loc2 = [alpha.index(coordinate2[1]), int(coordinate2[3])-1]
    loc3 = [alpha.index(coordinate3[1]), int(coordinate3[3])-1]
    ans1 = MATRIX[loc1[1]][loc1[0]]
    ans2 = MATRIX[loc2[1]][loc2[0]]
    ans3 = MATRIX[loc3[1]][loc3[0]]
    # print(ans1, ans2, ans3)
    driver.find_element(By.NAME, "message3").send_keys(ans1)
    driver.find_element(By.NAME, "message4").send_keys(ans2)
    driver.find_element(By.NAME, "message5").send_keys(ans3)
    button = driver.find_element(By.NAME, "OK")
    button.click()

    # 教務webシステム
    url = "https://kyomu2.gakumu.titech.ac.jp/Titech/Default.aspx"
    driver.get(url)

    # 施設予約
    url = "https://kyomu2.gakumu.titech.ac.jp/Titech/Common/FacilityReservation/Top.aspx"
    driver.get(url)

    # コート
    # time.sleep(10)
    # 予約状況確認
    weekly_dict = defaultdict()
    bodies_list = []
    count = 0
    for i in range(15):
        # today = datetime.datetime.today()
        today = getJST()
        if today.hour < 17:
            if not is_former: 
                if i < 7:
                    continue
        else:
            if i==0:
                continue
            else:
                count += 1
            if not is_former:
                if count <= 7:
                    continue
        search_date = today + datetime.timedelta(days=i)
        search_date_str = search_date.strftime('%Y%m%d')
        url = f"https://kyomu2.gakumu.titech.ac.jp/Titech/Common/FacilityReservation/Top.aspx?date={search_date_str}&bs=5&nofilter=1&m=d"
        driver.get(url)
        time.sleep(3)
        table = driver.find_element(By.CSS_SELECTOR, "table.tblDay")
        html = table.get_attribute("outerHTML")
        # print(html)
        df = pd.read_html(html)[0]
        # df.to_csv(f"./tmp/tmp_{i}.csv")
        _, season, daytype, = str(df["施設.2"][0]).split("：")
        key_season = ""
        if daytype == "平日":
            df = df.drop(columns=["12:15 -", "17:00 -"], index=3)
            a = np.where(np.array(df.isna()), 1, 0)
            if season == "夏時間":
                key_season = "summer_weekday"
            else: # 冬
                key_season = "winter_weekday"
        elif daytype == "土日祝":
            if season == "夏時間":
                df = df.drop(columns=["17:00 -"], index=3)
                key_season = "summer_holiday"
            else: # 冬
                df = df.drop(columns=["16:00 -"], index=3)
                key_season = "winter_holiday"
            # Bコートの予約が取れないため            
            a = np.where(np.array(df.isna()), 1, 0)
            df_str = df.copy()
            df_str.iloc[1,:]="teacher_only"
            a = np.where(np.array(df_str)=="teacher_only", a+100, a)
        
        new_dict = defaultdict(list)
        save_list = []
        for value, name in zip(a.T, df):
            if ":" in name:
                # 1 -> 予約なし、0 -> 予約あり
                tmp = list(map(int, value))
                # tmp[1] = 100
                new_dict[name] = tmp
                save_list.append(tmp)
        # print(save_list)
        text = make_body_day(search_date, today, new_dict, key_season)
        bodies_list.append(text)
        # print(text)
        key_tmp = f"{search_date_str[4:6]}/{search_date_str[6:8]}({num2youbi(search_date.strftime('%w'))})"
        weekly_dict[key_tmp] = save_list
        if today.hour < 17:
            if is_former:
                if i == 6:
                    break
        else:
            if is_former:
                if count == 7:
                    break
    
    # 変更分を参照する処理
    if is_difference:
        weekly_dict_mask = copy.deepcopy(weekly_dict)
        # 過去データの読み込み
        if is_former:
            if not os.path.exists("./zenkai_former.txt"):
                zenkai_dict = weekly_dict
                with open("./zenkai_former.txt", "wb") as f:
                    pickle.dump(zenkai_dict, f)
            else:
                with open("./zenkai_former.txt", "rb") as f:
                    zenkai_dict = pickle.load(f)
        else:
            if not os.path.exists("./zenkai_latter.txt"):
                zenkai_dict = weekly_dict
                with open("./zenkai_latter.txt", "wb") as f:
                    pickle.dump(zenkai_dict, f)
            else:
                with open("./zenkai_latter.txt", "rb") as f:
                    zenkai_dict = pickle.load(f)

        weekly_dict_mask, bodies_list = detect_difference(weekly_dict, weekly_dict_mask, zenkai_dict, bodies_list, is_former)

        return weekly_dict_mask, bodies_list
    else:
        return weekly_dict, bodies_list

def main_difference():
    #try:
    weekly_dict, bodies_list = scraping(is_former=True, is_difference=True)
    if weekly_dict == "end":
        return
    else:
        head_body = make_body_week(weekly_dict, is_difference=True, is_former=True)
    
    if is_debug:
        print(head_body, "\n\n", bodies_list)
    else:
        tweet(head_body, bodies_list)
    #except(Exception) as e:
     #   print(e)

def main_difference_later():
    # try:
    weekly_dict, bodies_list = scraping(is_former=False, is_difference=True)
    if weekly_dict == "end":
        return
    else:
        head_body = make_body_week(weekly_dict, is_difference=True, is_former=False)
    
    if is_debug:
        print(head_body, "\n\n", bodies_list)
    else:
        tweet(head_body, bodies_list)
    #except(Exception) as e:
     #   print(e)

def main_former():
    try:
        weekly_dict, bodies_list = scraping(is_former=True, is_difference=False)
        print(weekly_dict==True)
        if weekly_dict == "end":
            # print("here 1")
            return
        else:
            # print("here")
            head_body = make_body_week(weekly_dict, is_difference=False, is_former=True)
        
        if is_debug:
            print(head_body, "\n\n", bodies_list)
        else:
            tweet(head_body, bodies_list)
    except(Exception) as e:
        print(e)

def main_latter():
    try:
        weekly_dict, bodies_list = scraping(is_former=False, is_difference=False)
        if weekly_dict == "end":
            return
        else:
            head_body = make_body_week(weekly_dict, is_difference=False, is_former=False)
        
        if is_debug:
            print(head_body, "\n\n", bodies_list)
        else:
            tweet(head_body, bodies_list)
    except(Exception) as e:
        print(e)

def test():
    now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
    tweet(f"test at {now_jst.strftime('%H:%M')}", [])

if __name__=="__main__":
    # scraping()
    # main_former()
    # main_latter()
    # main_difference()
    # exit()
    if is_debug:
        main_difference()
        main_difference_later()
    # main_latter()
    exit()
    today = datetime.datetime.today()
    for i in range(7):
        today = today + datetime.timedelta(days=1)
        today_str = today.strftime('%Y%m%d')
        print(today_str)
    # pass
    # tweet("test 4", ["1","2","3"])
    # tweet(f"test {(datetime.datetime.now()).strftime('%H:%M')}", [])
    print((datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))).strftime('%H:%M'))
    # print([outer.split(",") for outer in outers])
