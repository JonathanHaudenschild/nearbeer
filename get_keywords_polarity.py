import requests
import statistics
from textblob import TextBlob
import re 
from rake_nltk import Rake
import nltk.data
import statistics


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
api_key = "AIzaSyB8IIGeILG6_IRsTHsvVvQJ3PyHZZ2N-sg"

def clean_review(review):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", review).split()) 
    
def get_review_sentiment(review):
	review_clean = clean_review(review)
	analysis = TextBlob(review_clean)
	return analysis.sentiment.polarity


def review_sentiment_keywords(bar_name):
    
    
    def clean_review(review):
    	return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", review).split()) 
    
    def get_review_sentiment(review):
    	review_clean = clean_review(review)
    	#print(review_clean)
    	analysis = TextBlob(review_clean) 
    	#review_sentiments.append(analysis.sentiment.polarity)
    	return analysis.sentiment.polarity
    
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


    keywords = ["guest", "people", "price", "staff", "waiter", "bartender", "beer", "atmosphere", "ambience", "music", "food"]
    keyword_polarity = [{"word": k, "pol": []} for k in keywords]

    def get_keyword_polarity(sentence):

    	#adds the polarity value of a keyword to the keywords_polarity array,  so we can get the mean polarity for the keyword later
    	def add_pol_to_keyword_pol(keyword, pol):
    		for e in keyword_polarity:
    			if e["word"] == keyword:
    				e["pol"].append(pol)

    	sentences = tokenizer.tokenize(sentence)

    	r = Rake()

    	for s in sentences:
    		#extract phrases -> no fill words
    		r.extract_keywords_from_text(s)
    		phrases = r.get_ranked_phrases()

    		for phrase in phrases:
    			for k in keywords:
    				#check if the keywords appear in the phrase
    				if k in phrase:
    					print(k)
    					polarity_phrase = get_review_sentiment(phrase)  
    					if polarity_phrase != 0.0:	#if the polarity != 0, the phrase is something like "good beers" -> save the polarity value in keyword_poopularity
    						add_pol_to_keyword_pol(k, polarity_phrase)
    						#print((phrase, polarity_phrase))
    						#print("\n")
    					else:	#if the polarity == 0, the phrase is the keyword itself, like 'beer'. so we take the polarity of the whole sentence -> save it in
    						polarity_sentence = get_review_sentiment(s)
    						add_pol_to_keyword_pol(k, polarity_sentence)
    						#print((sentence, polarity_sentence))
    						#print("\n")


    #calculate the keyword polarity for each review
    rake = Rake()
    for review in reviews_text:
    	print(review)
    	get_keyword_polarity(review)
    
    #filter out all keywords that weren't mentioned in the reviews
    list_pol_filtered = [e for e in keyword_polarity if e["pol"] != []]


    list_pol_mean = []

    #calculate the mean polarity for each mentioned keyword
    for r in list_pol_filtered:
    	pol_mean = round(statistics.mean(r["pol"]), 3)
    	list_pol_mean.append({"word": r["word"], "pol_mean": pol_mean})

    return list_pol_mean

keywords_pol_mean = review_sentiment_keywords("Flex")
print(keywords_pol_mean)


    	







#reviews_text2 = ["The guests were nice.", "Great atmosphere and guests", "great guests and delicious beers"]

#for review in reviews_text:
	#get_keyword_polarity(review)
#print(keyword_polarity)