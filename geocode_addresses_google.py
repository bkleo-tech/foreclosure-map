import pandas as pd
import requests
import os
import time

from dotenv import load_dotenv
load_dotenv()

CSV_PATH = 'Bank_Listings.csv'
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
CACHE_FILE = 'geocode_cache_google.csv'

def geocode_address(address, cache):
    if address in cache:
        return cache[address]
    params = {
        'address': address,
        'key': API_KEY,
        'region': 'ph',
    }
    resp = requests.get(GEOCODE_URL, params=params)
    if resp.status_code == 200:
        data = resp.json()
        if data['status'] == 'OK' and data['results']:
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            cache[address] = (lat, lng)
            time.sleep(0.2)  # Be nice to the API
            return lat, lng
    cache[address] = (None, None)
    time.sleep(0.2)
    return None, None

def main():
    df = pd.read_csv(CSV_PATH)
    cache = {}
    if os.path.exists(CACHE_FILE):
        cache_df = pd.read_csv(CACHE_FILE)
        cache = dict(zip(cache_df['address'], zip(cache_df['lat'], cache_df['lng'])))
    lats, lngs = [], []
    for addr in df['Address']:
        lat, lng = geocode_address(addr, cache)
        lats.append(lat)
        lngs.append(lng)
    df['Latitude'] = lats
    df['Longitude'] = lngs
    df.to_csv(CSV_PATH, index=False)
    # Save cache
    cache_df = pd.DataFrame([{'address': k, 'lat': v[0], 'lng': v[1]} for k, v in cache.items()])
    cache_df.to_csv(CACHE_FILE, index=False)
    print('Geocoding complete. Updated CSV with Latitude and Longitude.')

if __name__ == '__main__':
    main() 