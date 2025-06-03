from flask import Flask, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)
CSV_PATH = os.path.join(app.root_path, 'Bank_Listings.csv')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/properties')
def get_properties():
    df = pd.read_csv(CSV_PATH)
    properties = []
    for _, row in df.iterrows():
        def safe_get(col):
            val = row.get(col, None)
            return None if pd.isna(val) else val
        properties.append({
            'code': safe_get('Code'),
            'type': safe_get('Category'),
            'address': safe_get('Address'),
            'price': safe_get('Min Bid Price (PHP)'),
            'image': safe_get('Image'),
            'class': safe_get('Class'),
            'lot_area': safe_get('Lot Area (sqm)'),
            'floor_area': safe_get('Floor Area (sqm)'),
            'sales_officer': safe_get('Sales Officer'),
            'latitude': safe_get('Latitude'),
            'longitude': safe_get('Longitude')
        })
    return jsonify(properties)

if __name__ == '__main__':
    app.run(debug=True) 