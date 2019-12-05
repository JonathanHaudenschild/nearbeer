#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 13:33:21 2019

@author: eva
"""

import requests
import statistics
from textblob import TextBlob
import re 

def review_sentiment_mean(bar_name):

    api_key = "AIzaSyB8IIGeILG6_IRsTHsvVvQJ3PyHZZ2N-sg"
    
    
    review_sentiments = []
    
    def clean_review(review):
    	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", review).split()) 
    
    def get_review_sentiment(review):
    	review_clean = clean_review(review)
    	#print(review_clean)
    	analysis = TextBlob(review_clean) 
    	review_sentiments.append(analysis.sentiment.polarity)
    
    #get place id
    url_placeid = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key=" + api_key + "&inputtype=textquery&input=" + bar_name + "&fields=name,place_id"
    response_placeid = requests.get(url_placeid).json()
    #TODO: status respone status check
    
    place_id = response_placeid["candidates"][0]["place_id"]

    
    
    #get reviews
    url_reviews = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place_id + "&key=" + api_key

    data = requests.get(url_reviews).json()
    #TODO: status respone status check
    reviews = data["result"]["reviews"]
    reviews_text = [r["text"] for r in reviews]
    
    for r in reviews_text:
    	get_review_sentiment(r)
    
    return statistics.mean(review_sentiments)