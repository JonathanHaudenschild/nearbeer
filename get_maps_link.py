import requests

api_key = "AIzaSyB8IIGeILG6_IRsTHsvVvQJ3PyHZZ2N-sg"

lat_start = "48.135087"
lon_start = "11.549746"

lat_end = "48.133053"
lon_end = "11.557680"

url_map = "https://www.google.com/maps/dir/?api=1&origin=" + lat_start + "," + lon_start + "&destination=" + lat_end + "," + lon_end
print(url_map)



