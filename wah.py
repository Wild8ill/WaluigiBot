#! /usr/bin/env python3

import tweepy
from telegram.ext import Updater
import telegram
from datetime import datetime, timedelta
from random import randint
import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_wishlist(username):
    url = "https://store.steampowered.com/wishlist/id/{!s}/#sort=order".format(username)
    print(url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html.parser')
    wishlist_games = []
    for link in soup.find_all('script'):
        if "g_rgAppInfo" in link.text:
            array_of_vars = link.text.splitlines()
            for each in array_of_vars:
                if "g_rgAppInfo" in each:
                    formatted_string = each.strip()[18:len(each)-2] # exists for a reason, the reason is too long to explain
                    objects = json.loads(formatted_string)
                    for each_game in objects:
                        name_of_the_game =(objects[each_game]["name"])
			#format the name to aid in searching tweets
                        name_of_the_game = re.sub('[^A-Za-z0-9\'.,! ]','',name_of_the_game)
                        name_of_the_game = name_of_the_game.lower().strip()
			#add completed string to the list
                        wishlist_games.append(name_of_the_game)
    return wishlist_games


def verify_tweets(tweets,whitelist,blacklist,users):
    for tweet in tweets:
        tweet_text = tweet.text.lower()
        state = "False"
        for each_word in whitelist:
            if each_word in tweet_text:
                state = "True"
                matched_word = each_word
                print(tweet_text)
                print(matched_word)
        for each_word in blacklist:
            if each_word in tweet_text:
                state = "False"
        userstatus = "False"
        for each_user in users:
            if each_user == tweet.user.name:
                userstatus = "True"
                break
        #setup waluigi sayings
        walmod = ["WALUIGI NUMBER ONEEEE!!","WAH!","Wahahaha! Waluigi, number one!","Waluigi win!","Wah hah hah waah!","Waluigi time!"]
        #setup list of chat users
        chatarray = []
        with open("userids.txt", "r") as f:
            for line in f:
                chatarray.append(line)
        if state == "True" and userstatus == "True":
            textmessage = walmod[randint(0,len(walmod)-1)] +"\n" + tweet.text
            global stored_messages
            global stored_topics
            final_check = message_intersection(stored_messages,tweet.text,matched_word)
            stored_messages.append(tweet.text)
            stored_topics.append(matched_word)
            if final_check:
                for user in chatarray:
                    try:
                        wal_bot.send_message(chat_id=user.rstrip(), text=textmessage)
                    except:
                        print(user)


def message_intersection(list_of_confirmed_messages,message_to_check,word_to_check):
    check_set = set(message_to_check.split())
    global stored_topics
    for each_message in list_of_confirmed_messages:
        conf_set = set(each_message.split())
        crossover = check_set.intersection(conf_set)
        if crossover == set():
            print("Percent Significance : 0%")
            return True
        percent_sig = (len(crossover)/len(conf_set)*100)
        print("Percent Significance :"+str(percent_sig))
        if percent_sig > 65:
            return False
        else:
            for each_word in stored_topics:
                if each_word == word_to_check:
                    return False
            return True


# Twitter API credentials
consumer_key = "REDACTED"
consumer_secret = "REDACTED"
access_key = "REDACTED"
access_secret = "REDACTED"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

# Initialising a telegram bot

wal_bot = telegram.Bot("REDACTED")
updater = Updater("REDACTED")
dispatcher = updater.dispatcher
print(wal_bot.get_me())

# Creates and initialises the required whitelist, blacklist, and verified_users variables

whitelist = [" free ","destiny","cuphead","zelda","star wars","sonic","xenoblade"]
blacklist = ["us psn","best buy","free shipping","X1"]
verified_users = ["Wario64","Cheap Ass Gamer"]
stored_messages = [""]
stored_topics = [""]

# Gets last checked tweet id to stop spam

with open("recenttweet.txt", "r") as f:
    read_data = f.read()
            
public_tweets = api.home_timeline(read_data) # Gets all new tweets from timeline

if public_tweets == []: # Gf there are no new ones exits the program
    print("No new tweets")
    exit(0)

firsttweet = public_tweets[0] # The first (at the top aka most recent) tweet, and the one we will
# use to ensure no spam
with open("recenttweet.txt", "w") as f:
    f.write(str(firsttweet.id))

# Runs functions

whitelist += scrape_wishlist("Wild8ill")
verify_tweets(public_tweets,whitelist,blacklist,verified_users)

