import requests
from datetime import date
import VenueInfoBeer as vib

# url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + currentLocation + "&radius=" + radius "&types=bar&key=AIzaSyB8IIGeILG6_IRsTHsvVvQJ3PyHZZ2N-sg"
# response = requests.get(url)
location = "48.097480,11.580790"
client_id_foursquare = "W3NTNWINQN5HTRAS2WADYGU1R3REZFY0YCTNXKD3NC2YCMJI"
client_secret_foursquare = "JDLHAQ35QAK5WBX512IC1YISVS13HIWFC5JZD2EKZPSBPL1J"
foursquare_v2_api = "https://api.foursquare.com/v2/"
date = date.today().strftime("%Y%m%d")
category_id_bar = "4bf58dd8d48988d116941735"
print(date)

foursquare_search_bar = "{foursquare_v2_api}venues/search?ll={loc}&client_id={client_id}&client_secret={client_secret}" \
                        "&v={date}&categoryId={category}".format(foursquare_v2_api=foursquare_v2_api, loc=location,
                                                                 client_id=client_id_foursquare,
                                                                 client_secret=client_secret_foursquare, date=date,
                                                                 category=category_id_bar)
untapped_api = "https://api.untappd.com/v4/"
client_secret_untapped = "A975C849FCC57D8A36D493B00F5B08714EF78209"
client_id_untapped = "4998D655D6F90D1EA6B8DCFEDECDE30714D9FEB1"


def getBeerSearch(beer_name):
    url = "{untapped_api}search/beer?client_secret={client_secret}&client_id={client_id}&q='{beer_name}'" \
        .format(untapped_api=untapped_api, client_secret=client_secret_untapped, client_id=client_id_untapped,
                beer_name=beer_name)
    return requests.get(url)


def getVenueIdUntapped(foursquare_id):
    url = "{untapped_api}venue/foursquare_lookup/{foursquare_id}?&client_secret={client_secret}&client_id={client_id}" \
        .format(untapped_api=untapped_api, foursquare_id=foursquare_id, client_secret=client_secret_untapped,
                client_id=client_id_untapped)
    print(url)
    return requests.get(url)


def getVenueInfo(untapped_id):
    url = "{untapped_api}venue/info/{untapped_id}?client_secret={client_secret}&client_id={client_id}" \
        .format(untapped_api=untapped_api, untapped_id=untapped_id, client_secret=client_secret_untapped,
                client_id=client_id_untapped)
    return requests.get(url)

def getMostPopularBeer(beer_name):
    beer_response = getBeerSearch(beer_name)
    if beer_response.status_code == 200:
        beer_info = beer_response.json()["response"]["beers"]["items"][0]["beer"]
        return beer_info["bid"], beer_info["beer_name"], beer_info["beer_abv"]
    else:
        print(beer_response)


def getBeerFromNearestVenue(beer_name):
    beer_id, name, abv = getMostPopularBeer(beer_name)
    print("\n Beer name, id:")
    print(name, beer_id)
    foursquare_response = requests.get(foursquare_search_bar)
    if foursquare_response.status_code == 200:
        venues = foursquare_response.json()["response"]["venues"]
        for venue in venues:
            print("\n Venue in for:")
            print(venue["name"])
            foursquare_id = venue["id"]
            untapped_response = getVenueIdUntapped(foursquare_id)
            if untapped_response.status_code == 200:
                untapped_id = untapped_response.json()["response"]["venue"]["items"][0]["venue_id"]
                venue_info = getVenueInfo(untapped_id)
                if venue_info.status_code == 200:
                    venue_medias = venue_info.json()["response"]["venue"]["media"]["items"]
                    for venue_media in venue_medias:
                        beer_id_media = venue_media["beer"]["bid"]
                        print("\nBeer name in for, id:")
                        print(venue_media["beer"]["beer_name"], beer_id_media)
                        if beer_id_media == beer_id:
                            print("\n\nBar Found:")
                            return venue["name"], venue["location"]["address"]
                else:
                    print(venue_info)
            else:
                print(untapped_response)
    else:
        print(foursquare_response)

"""
response = requests.get(foursquare_search_bar)
print(response.status_code)
if response.status_code == 200:
    response = response.json()
    venues = response["response"]["venues"]
    print(len(venues))
    for i in range(0, 1):
        foursquare_id = venues[i]['id']
        print(foursquare_id)
        response_untapped = getVenueIdUntapped(foursquare_id)
        print(response_untapped)
        if response_untapped.status_code == 200:
            print(response_untapped.json()["response"]["venue"]["items"][0]["venue_name"])
            untapped_id = response_untapped.json()["response"]["venue"]["items"][0]["venue_id"]
            venue_info = getVenueInfo(untapped_id)
            if venue_info.status_code == 200:
                venue_info = venue_info.json()["response"]["venue"]
                venue_media = venue_info["media"]["items"][4]
                media_beer = venue_media["beer"]
                print(media_beer)"""

def getBeerFromNearestVenueDic(beer_name, beer_dic):
    beer_id, name, abv = getMostPopularBeer(beer_name)
    print("\n Beer name, id:")
    print(name, beer_id)
    print(beer_dic)
    for venue in beer_dic:
        print(venue)
        print("Search venue "+venue)
        for beer in beer_dic[venue]["beers"]:
            print("Has "+beer["name"])
            if beer["id"] == beer_id:
                print(beer)
                print(beer_dic[venue])
                print("Found "+beer["name"]+"at "+venue+" location: "+beer_dic[venue]["address"])
    """
    foursquare_response = requests.get(foursquare_search_bar)
    if foursquare_response.status_code == 200:
        venues = foursquare_response.json()["response"]["venues"]
        for venue in venues:
            print("\n Venue in for:")
            print(venue["name"])
            foursquare_id = venue["id"]
            untapped_response = getVenueIdUntapped(foursquare_id)
            if untapped_response.status_code == 200:
                untapped_id = untapped_response.json()["response"]["venue"]["items"][0]["venue_id"]
                venue_info = getVenueInfo(untapped_id)
                if venue_info.status_code == 200:
                    venue_medias = venue_info.json()["response"]["venue"]["media"]["items"]
                    for venue_media in venue_medias:
                        beer_id_media = venue_media["beer"]["bid"]
                        print("\nBeer name in for, id:")
                        print(venue_media["beer"]["beer_name"], beer_id_media)
                        if beer_id_media == beer_id:
                            print("\n\nBar Found:")
                            return venue["name"], venue["location"]["address"]
                else:
                    print(venue_info)
            else:
                print(untapped_response)
    else:
        print(foursquare_response)"""

venue_info_dic = vib.getVenueInfoDic()
print(getBeerFromNearestVenueDic("Winkler Naturradler", venue_info_dic))
print(getBeerFromNearestVenueDic("Franziskaner Weißbier", venue_info_dic))
print(getBeerFromNearestVenueDic("Augustiner Helles", venue_info_dic))
print(getBeerFromNearestVenueDic("Giesinger Bräu Helles", venue_info_dic))