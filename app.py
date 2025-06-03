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
        # Helper function to safely get data and convert NaN to None
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
    # Get the port from the environment variable, default to 8080 for local development
    port = int(os.environ.get('PORT', 8080))
    # Run the app on all interfaces and the specified port
    app.run(host='0.0.0.0', port=port, debug=True) 