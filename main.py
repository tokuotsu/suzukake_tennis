#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
from create_tweet import tweet

import time
import datetime

# import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
    print(ans1, ans2, ans3)
    driver.find_element(By.NAME, "message3").send_keys(ans1)
    driver.find_element(By.NAME, "message4").send_keys(ans2)
    driver.find_element(By.NAME, "message5").send_keys(ans3)
    button = driver.find_element(By.NAME, "OK")
    button.click()

    # 予約状況確認
    today = datetime.datetime.today()
    for i in range(7):
        today = today + datetime.timedelta(days=1)
        today_str = today.strftime('%Y%m%d')
        url = f"https://kyomu2.gakumu.titech.ac.jp/Titech/Common/FacilityReservation/Top.aspx?date={today_str}&bs=5&nofilter=1&m=d"
        driver.get(url)

    time.sleep(10)

if __name__=="__main__":
    scraping()
    today = datetime.datetime.today()
    for i in range(7):
        today = today + datetime.timedelta(days=1)
        today_str = today.strftime('%Y%m%d')
        print(today_str)
    # pass
    # tweet("test 4", ["1","2","3"])
    tweet(f"test {(datetime.datetime.now()).strftime('%H:%M')}", [])
    print((datetime.datetime.now()).strftime('%H:%M'))
    # print([outer.split(",") for outer in outers])
