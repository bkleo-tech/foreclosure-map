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
        properties.append({
            'code': row['Code'],
            'type': row['Category'],
            'address': row['Address'],
            'price': row['Min Bid Price (PHP)'],
            'image': row['Image'] if 'Image' in row and not pd.isna(row.get('Image', None)) else '',
            'class': row['Class'],
            'lot_area': row['Lot Area (sqm)'],
            'floor_area': row['Floor Area (sqm)'],
            'sales_officer': row['Sales Officer'],
            'latitude': row['Latitude'] if 'Latitude' in row and not pd.isna(row['Latitude']) else None,
            'longitude': row['Longitude'] if 'Longitude' in row and not pd.isna(row['Longitude']) else None
        })
    return jsonify(properties)

if __name__ == '__main__':
    # Get the port from the environment variable, default to 8080 for local development
    port = int(os.environ.get('PORT', 8080))
    # Run the app on all interfaces and the specified port
    app.run(host='0.0.0.0', port=port, debug=True) 