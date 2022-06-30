#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
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

# ローカルでは必要
# import chromedriver_binary

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

def scraping():
    global STUDENT_ID
    global PASSWORD
    global MATRIX
    url = "https://portal.nap.gsic.titech.ac.jp/GetAccess/Login?Template=userpass_key&AUTHMETHOD=UserPassword"
    options = Options()
    # ブラウザ表示の有無
    # options.add_argument('--headless')
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
    for i in range(14):
        # today = datetime.datetime.today()
        today = getJST()
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
        
        new_dict = defaultdict(list)
        save_list = []
        for value, name in zip(np.array(df.isna().T), df):
            if ":" in name:
                # 1 -> 予約なし、0 -> 予約あり
                new_dict[name] = list(map(int, value))
                save_list.append(list(map(int, value)))
        text = make_body_day(search_date, today, new_dict, key_season)
        bodies_list.append(text)
        # print(text)
        key_tmp = f"{search_date_str[4:6]}/{search_date_str[6:8]}({num2youbi(search_date.strftime('%w'))})"
        weekly_dict[key_tmp] = save_list
        # break
    # if not os.path.exists("./zenkai.txt"):
    #     dic_zenkai = weekly_dict
    #     with open("./zenkai.txt", "wb") as f:
    #         pickle.dump(dic_zenkai, f)
    # else:
    #     with open("./zenkai.txt", "rb") as f:
    #         dic_zenkai = pickle.load(f)

    return weekly_dict, bodies_list

def main_former():
    weekly_dict, bodies_list = scraping()
    head_body = make_body_week(weekly_dict, is_fomer=True)
    tweet(head_body, bodies_list[:7])

def main_latter():
    weekly_dict, bodies_list = scraping()
    head_body = make_body_week(weekly_dict, is_fomer=False)
    tweet(head_body, bodies_list[7:])

def test():
    now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9), 'JST'))
    tweet(f"test at {now_jst.strftime('%H:%M')}", [])

if __name__=="__main__":
    scraping()
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
