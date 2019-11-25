import requests
from datetime import date


location = "48.097480,11.580790"
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
    print(url)
    return requests.get(url)


def getVenueInfo(untapped_id):
    url = "{untapped_api}venue/info/{untapped_id}?client_secret={client_secret}&client_id={client_id}" \
        .format(untapped_api=untapped_api, untapped_id=untapped_id, client_secret=client_secret_untapped,
                client_id=client_id_untapped)
    return requests.get(url)

venue_info_beer = {}
def getVenueInfoDic():
    foursquare_response = requests.get(foursquare_search_bar)
    if foursquare_response.status_code == 200:
        venues = foursquare_response.json()["response"]["venues"]
        for number, venue in enumerate(venues):
            if number > 20:
                return venue_info_beer
            else:
                print("\n Venue in for:")
                print(venue["name"])
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
                        print(venue_info)
                else:
                    print(untapped_response)
    else:
        print(foursquare_response)
    return venue_info_beer
