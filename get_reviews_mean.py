#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import statistics
from textblob import TextBlob 
import re 

place_id = "ChIJxfxSz4t1nkcRLxq9ze1wwak"
place_id2 = "ChIJq6QFKAB2nkcRwvNg8E5WHXE"
place_id3 = "ChIJB86FEk_fnUcRt3_hOgcbEdY"
api_key = "AIzaSyB8IIGeILG6_IRsTHsvVvQJ3PyHZZ2N-sg"
url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place_id3 + "&key=" + api_key

review_sentiments = []

def clean_review(review):
	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", review).split()) 

def get_review_sentiment(review):
	review_clean = clean_review(review)
	#print(review_clean)
	analysis = TextBlob(review_clean) 
	review_sentiments.append(analysis.sentiment.polarity)

data = requests.get(url).json()

reviews = data["result"]["reviews"]

reviews_text = [r["text"] for r in reviews]

for r in reviews_text:
	get_review_sentiment(r)

return statistics.mean(review_sentiments)
