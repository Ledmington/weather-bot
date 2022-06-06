from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="weather-bot")
location = geolocator.geocode("Riccione")
print(location.address)
print((location.latitude, location.longitude))
print(location.raw)

with open("weather-key.txt", "r") as f:
    api_key = f.read()
print(api_key)