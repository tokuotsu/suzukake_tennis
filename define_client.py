#! /usr/bin/python3
# -*- coding: utf-8 -*-
from config import CONFIG
from requests_oauthlib import OAuth1Session
# --------------------------------------------------------------------
def define_client_proc():
    CONSUMER_KEY = CONFIG["CONSUMER_KEY"]
    CONSUMER_SECRET = CONFIG["CONSUMER_SECRET"]
    ACCESS_TOKEN = CONFIG["ACCESS_TOKEN"]
    ACCESS_TOKEN_SECRET = CONFIG["ACCESS_SECRET"]
    # OAuthの認証オブジェクトの作成
    twitter = OAuth1Session(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET)
    return twitter