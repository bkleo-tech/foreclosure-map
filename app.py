from flask import Flask, render_template, send_from_directory, jsonify
import os
import pandas as pd

app = Flask(__name__)

CSV_PATH = os.path.join(app.root_path, 'Bank_Listings.csv')

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to get property data
@app.route('/api/properties')
def get_properties():
    df = pd.read_csv(CSV_PATH)
    # Only return relevant fields
    properties = []
    for _, row in df.iterrows():
        properties.append({
            'code': row['Code'],
            'type': row['Category'],
            'address': row['Address'],
            'price': row['Min Bid Price (PHP)'],
            'image': row['Image'] if 'Image' in row and not pd.isna(row['Image']) else '',
            'class': row['Class'],
            'lot_area': row['Lot Area (sqm)'],
            'floor_area': row['Floor Area (sqm)'],
            'sales_officer': row['Sales Officer']
            # Add lat/lng here if available in the future
        })
    return jsonify(properties)

# Serve images from static/images
@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/images'), filename)

if __name__ == '__main__':
    app.run(debug=True) 