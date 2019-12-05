#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 13:31:58 2019

@author: eva
"""

import requests
from datetime import date
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

location = "48.150848,11.577850"
client_id_foursquare = "W3NTNWINQN5HTRAS2WADYGU1R3REZFY0YCTNXKD3NC2YCMJI"
client_secret_foursquare = "JDLHAQ35QAK5WBX512IC1YISVS13HIWFC5JZD2EKZPSBPL1J"
foursquare_v2_api = "https://api.foursquare.com/v2/"
date = date.today().strftime("%Y%m%d")
category_id_bar = "4bf58dd8d48988d116941735"

foursquare_search_bar = "{foursquare_v2_api}venues/search?ll={loc}&client_id={client_id}&client_secret={client_secret}" \
                        "&v={date}&categoryId={category}".format(foursquare_v2_api=foursquare_v2_api, loc=location,
                                                                 client_id=client_id_foursquare,
                                                                 client_secret=client_secret_foursquare, date=date,
                                                                 category=category_id_bar)
untapped_api = "https://api.untappd.com/v4/"
client_secret_untapped = "A975C849FCC57D8A36D493B00F5B08714EF78209"
client_id_untapped = "4998D655D6F90D1EA6B8DCFEDECDE30714D9FEB1"


def getVenueIdUntapped(foursquare_id):
    url = "{untapped_api}venue/foursquare_lookup/{foursquare_id}?&client_secret={client_secret}&client_id={client_id}" \
        .format(untapped_api=untapped_api, foursquare_id=foursquare_id, client_secret=client_secret_untapped,
                client_id=client_id_untapped)
    logger.info("url untapped "+url)
    return requests.get(url)


def getVenueInfo(untapped_id):
    url = "{untapped_api}venue/info/{untapped_id}?client_secret={client_secret}&client_id={client_id}" \
        .format(untapped_api=untapped_api, untapped_id=untapped_id, client_secret=client_secret_untapped,
                client_id=client_id_untapped)
    logger.info("Foursquare url"+url)
    return requests.get(url)

venue_info_beer = OrderedDict()
def createVenueInfoDic():
    counter = 0
    logger.info("in getVenueInfoDic")
    logger.info("current venue dic: "+str(venue_info_beer))
    foursquare_response = requests.get(foursquare_search_bar)
    if foursquare_response.status_code == 200:
        venues = foursquare_response.json()["response"]["venues"]
        for number, venue in enumerate(venues):
            logger.info("in venue number: "+ str(number))
            if number > (len(venue_info_beer)) and counter < 10:
                counter += 1
                foursquare_id = venue["id"]
                untapped_response = getVenueIdUntapped(foursquare_id)
                if untapped_response.status_code == 200:
                    untapped_id = untapped_response.json()["response"]["venue"]["items"][0]["venue_id"]
                    venue_info = getVenueInfo(untapped_id)
                    if venue_info.status_code == 200:
                        venue_info_beer[venue["name"]] = {"address": venue["location"]["address"], "beers": []}
                        venue_medias = venue_info.json()["response"]["venue"]["media"]["items"]
                        for venue_media in venue_medias:
                            beer_id_media = venue_media["beer"]["bid"]
                            venue_info_beer[venue["name"]]["beers"].append({"name": venue_media["beer"]["beer_name"],
                                                                            "id": beer_id_media})
                    else:
                        return "Sorry, i can't search for bars right now. Please ask me to search for bars again later."
                else:
                    return "Sorry, i can't search for bars right now. Please ask me to search for bars again later."
    else:
        return "Sorry, i can't search for bars right now. Please ask me to search for bars again later."
    return venue_info_beer

def getVenueInfoDic():
    logger.info("venue_info_beer is: "+str (venue_info_beer))
    return venue_info_beer


def getBeerSearch(beer_name):
    url = "{untapped_api}search/beer?client_secret={client_secret}&client_id={client_id}&q='{beer_name}'" \
        .format(untapped_api=untapped_api, client_secret=client_secret_untapped, client_id=client_id_untapped,
                beer_name=beer_name)
    return requests.get(url)



def getMostPopularBeer(beer_name):
    beer_response = getBeerSearch(beer_name)
    if beer_response.status_code == 200:
        beer_info = beer_response.json()["response"]["beers"]["items"][0]["beer"]
        return beer_info["bid"], beer_info["beer_name"], beer_info["beer_abv"]
    else:
        logger.info(str(beer_response))
        return "Sorry i cant search for bar with your beer right know. Please ask me again later."


def getBeerFromNearestVenueDic(beer_name):
    result = getMostPopularBeer(beer_name)
    if(type(result) == str):
        return result
    else:
        beer_id, name, abv = result
        logger.info("\n Beer name, id:")
        logger.info(str(name) + " " + str(beer_id))
        logger.info(str(venue_info_beer))
        for venue in venue_info_beer:
            logger.info("Search venue "+venue)
            for beer in venue_info_beer[venue]["beers"]:
                logger.info("Has "+ str(beer["name"]))
                if beer["id"] == beer_id:
                    logger.info(str(beer))
                    logger.info(str(venue_info_beer[venue]))
                    logger.info("Found "+beer["name"]+"at "+venue+" location: "+venue_info_beer[venue]["address"])
                    return beer, venue
    return "Sorry, your beer is not avaiable in the bars near you. Please ask for an other beer or do somthing diffrent"