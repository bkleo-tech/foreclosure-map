import pandas as pd
import requests
import time
import os

CSV_PATH = 'Bank_Listings.csv'
USER_AGENT = 'foreclosure-map-cs50/1.0 (your_email@example.com)'
GEOCODE_URL = 'https://nominatim.openstreetmap.org/search'
CACHE_FILE = 'geocode_cache.csv'

def geocode_address(address, cache):
    if address in cache:
        return cache[address]
    params = {
        'q': address,
        'format': 'json',
        'countrycodes': 'ph',
        'limit': 1,
    }
    headers = {'User-Agent': USER_AGENT}
    resp = requests.get(GEOCODE_URL, params=params, headers=headers)
    if resp.status_code == 200 and resp.json():
        lat = resp.json()[0]['lat']
        lon = resp.json()[0]['lon']
        cache[address] = (lat, lon)
        time.sleep(1)  # Be nice to the API
        return lat, lon
    else:
        cache[address] = (None, None)
        time.sleep(1)
        return None, None

def main():
    df = pd.read_csv(CSV_PATH)
    cache = {}
    if os.path.exists(CACHE_FILE):
        cache_df = pd.read_csv(CACHE_FILE)
        cache = dict(zip(cache_df['address'], zip(cache_df['lat'], cache_df['lon'])))
    lats, lons = [], []
    for addr in df['Address']:
        lat, lon = geocode_address(addr, cache)
        lats.append(lat)
        lons.append(lon)
    df['Latitude'] = lats
    df['Longitude'] = lons
    df.to_csv(CSV_PATH, index=False)
    # Save cache
    cache_df = pd.DataFrame([{'address': k, 'lat': v[0], 'lon': v[1]} for k, v in cache.items()])
    cache_df.to_csv(CACHE_FILE, index=False)
    print('Geocoding complete. Updated CSV with Latitude and Longitude.')

if __name__ == '__main__':
    main() 