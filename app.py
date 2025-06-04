from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import pandas as pd
import os
import requests # Import requests for geocoding
import time # Import time for rate limiting
import functools # Import functools at the top
from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy

from dotenv import load_dotenv # Keep dotenv for local testing if you use a .env file
load_dotenv()

# --- Configuration --- #
SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key_that_should_be_changed') # Add a secret key for sessions
# Database Configuration - Set this environment variable! (e.g., in .env or Railway variables)
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@host:port/dbname') # Placeholder URI
# Consider using DATABASE_URL which Railway often provides automatically

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password') # CHANGE THIS!

# Define the Flask app instance AFTER configuration variables
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY # Configure secret key
# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable modification tracking for performance
db = SQLAlchemy(app)

# Now define paths and other configurations that use the 'app' instance
CSV_PATH = os.path.join(app.root_path, 'Bank_Listings.csv')
GOOGLE_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY') # Get API key from environment
GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

# --- Database Model --- #
class Property(db.Model):
    __tablename__ = 'properties'
    # Assuming 'Code' is unique and can serve as a primary key
    # If not, add an 'id' column: db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, primary_key=True)
    category = db.Column(db.String, nullable=True)
    class_type = db.Column(db.String, nullable=True, name='class') # Use a different name if 'class' is reserved
    address = db.Column(db.String, nullable=True)
    lot_area = db.Column(db.Float, nullable=True)
    floor_area = db.Column(db.Float, nullable=True)
    min_bid_price_php = db.Column(db.Float, nullable=True, name='min_bid_price_(php)') # Handle column name with special chars
    sales_officer = db.Column(db.String, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    image = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<Property {self.code}>"

    # Helper method to convert model instance to dictionary
    def to_dict(self):
        return {
            'code': self.code,
            'category': self.category if self.category is not None else "N/A",
            'class': self.class_type,
            'address': self.address,
            'lot_area': self.lot_area if self.lot_area is not None else "N/A",
            'floor_area': self.floor_area if self.floor_area is not None else "N/A",
            'min_bid_price_(php)': self.min_bid_price_php if self.min_bid_price_php is not None else "N/A",
            'sales_officer': self.sales_officer if self.sales_officer is not None else "N/A",
            'latitude': self.latitude,
            'longitude': self.longitude,
            'image': self.image if self.image is not None else "N/A"
        }

# --- Data Storage (In-Memory) --- #
# This will be replaced by database interaction
# all_properties_data = [] # Remove or comment out later

# --- Geocoding Function --- #
def geocode_address_google(address):
    """Geocodes an address using Google Maps Geocoding API."""
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_MAPS_API_KEY not set. Geocoding will not work.")
        return None, None

    params = {
        'address': address,
        'key': GOOGLE_API_KEY,
        'region': 'ph', # Specify region for better results
    }
    try:
        resp = requests.get(GEOCODE_URL, params=params)
        resp.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = resp.json()
        if data['status'] == 'OK' and data['results']:
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']
            time.sleep(0.1) # Add a small delay to respect API rate limits
            return lat, lng
        elif data['status'] == 'ZERO_RESULTS':
             print(f"Geocoding returned zero results for: {address}")
             return None, None
        else:
            print(f"Geocoding error for {address}: {data['status']}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Request error during geocoding {address}: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during geocoding {address}: {e}")
        return None, None

# --- Initial Data Load --- #
def load_initial_data_to_db():
    """Loads initial data from the CSV into the database if the table is empty."""
    try:
        # Check if the table is empty
        if Property.query.first() is None:
            print(f"Database table 'properties' is empty. Loading initial data from {CSV_PATH}...")
            df = pd.read_csv(CSV_PATH)
            properties_to_add = []
            for index, row in df.iterrows():
                # Create a Property object from the row
                # Use .get() with default None to handle potential missing columns gracefully
                property_obj = Property(
                    code=row.get('Code'),
                    category=row.get('Category') if pd.notna(row.get('Category')) else None,
                    class_type=row.get('Class'),
                    address=row.get('Address'),
                    lot_area=row.get('Lot Area (sqm)') if pd.notna(row.get('Lot Area (sqm)')) else None,
                    floor_area=row.get('Floor Area (sqm)') if pd.notna(row.get('Floor Area (sqm)')) else None,
                    min_bid_price_php=row.get('Min Bid Price (PHP)') if pd.notna(row.get('Min Bid Price (PHP)')) else None,
                    sales_officer=row.get('Sales Officer') if pd.notna(row.get('Sales Officer')) else None,
                    # Geocoding is now handled during upload, but can initially load existing lat/lng
                    latitude=row.get('Latitude') if pd.notna(row.get('Latitude')) else None,
                    longitude=row.get('Longitude') if pd.notna(row.get('Longitude')) else None,
                    image=row.get('Image') if pd.notna(row.get('Image')) else None
                )
                properties_to_add.append(property_obj)

            db.session.bulk_save_objects(properties_to_add)
            db.session.commit()
            print(f"Initial {len(properties_to_add)} properties loaded into the database.")
        else:
            print("Database table 'properties' is not empty. Skipping initial data load from CSV.")
    except FileNotFoundError:
        print(f"Warning: {CSV_PATH} not found. Cannot load initial data.")
    except Exception as e:
        db.session.rollback()
        print(f"Error loading initial data to database: {e}")

# --- Database Initialization --- #
# This should ideally be run separately, but for simplicity, we can create tables on first request
# or before the first request. A better way for production is Flask-Migrate.
with app.app_context():
    db.create_all()
    # Load initial data into DB after creating tables, only if table is empty
    load_initial_data_to_db()

# --- Authentication Decorator --- #
def login_required(view):
    """Decorator to protect admin routes."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# --- Routes --- #
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/properties')
def get_properties():
    # Fetch data from the database
    properties_from_db = Property.query.all()
    # Convert SQLAlchemy objects to dictionaries for JSON response using to_dict method
    properties_for_json = [prop.to_dict() for prop in properties_from_db]

    # jsonify correctly converts Python None to JSON null
    return jsonify(properties_for_json)

@app.route('/admin')
@login_required
def admin():
    """Admin page for uploading files."""
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html') # Render login form on GET

@app.route('/logout')
def logout():
    """Logout route."""
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_csv():
    """Handles CSV upload, geocoding, and updates the database."""
    if 'csv_file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['csv_file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and file.filename.endswith('.csv'):
        try:
            from io import BytesIO
            file_content = file.read()
            df = pd.read_csv(BytesIO(file_content))

            # Ensure required columns exist, defaulting to None if not
            required_cols = [
                'Code', 'Category', 'Class', 'Address', 'Lot Area (sqm)', 
                'Floor Area (sqm)', 'Min Bid Price (PHP)', 'Sales Officer', 
                'Latitude', 'Longitude', 'Image'
            ]
            for col in required_cols:
                 if col not in df.columns:
                      df[col] = None

            # Store codes from the uploaded CSV for deletion logic later
            uploaded_codes = set(df['Code'].dropna().astype(str).tolist())

            print("Starting geocoding and database update for new data...")
            geocoded_count = 0
            updated_count = 0
            inserted_count = 0
            errors = []

            for index, row in df.iterrows():
                code = row.get('Code')
                if pd.isna(code) or code == '':
                    errors.append(f"Row {index + 1}: Missing or empty 'Code'. Skipping row.")
                    print(errors[-1])
                    continue # Skip rows without a valid code

                # Find existing property by code
                property_obj = Property.query.filter_by(code=str(code)).first()

                # Geocode if Latitude or Longitude is missing or is NaN
                lat = row.get('Latitude')
                lng = row.get('Longitude')
                geocode_needed = pd.isna(lat) or pd.isna(lng)

                if geocode_needed:
                     address = row.get('Address')
                     if address:
                         geocoded_lat, geocoded_lng = geocode_address_google(address)
                         if geocoded_lat is not None and geocoded_lng is not None:
                             lat = geocoded_lat
                             lng = geocoded_lng
                             geocoded_count += 1
                             print(f"Geocoded \"{address}\" to ({lat}, {lng}) for code {code}")
                         else:
                              errors.append(f"Row {index + 1}: Could not geocode address for code {code}: {address}")
                              print(errors[-1])

                # Prepare data for database update/insert
                data_to_save = {
                    'code': str(code), # Ensure code is string
                    'category': row.get('Category') if pd.notna(row.get('Category')) else None,
                    'class_type': row.get('Class') if pd.notna(row.get('Class')) else None,
                    'address': row.get('Address') if pd.notna(row.get('Address')) else None,
                    'lot_area': row.get('Lot Area (sqm)') if pd.notna(row.get('Lot Area (sqm)')) else None,
                    'floor_area': row.get('Floor Area (sqm)') if pd.notna(row.get('Floor Area (sqm)')) else None,
                    'min_bid_price_php': row.get('Min Bid Price (PHP)') if pd.notna(row.get('Min Bid Price (PHP)')) else None,
                    'sales_officer': row.get('Sales Officer') if pd.notna(row.get('Sales Officer')) else None,
                    'latitude': lat if pd.notna(lat) else None,
                    'longitude': lng if pd.notna(lng) else None,
                    'image': row.get('Image') if pd.notna(row.get('Image')) else None
                }
                
                # Ensure numeric types are actually numbers or None
                for num_col in ['lot_area', 'floor_area', 'min_bid_price_php', 'latitude', 'longitude']:
                     val = data_to_save.get(num_col)
                     if val is not None:
                          try:
                               data_to_save[num_col] = float(val)
                          except (ValueError, TypeError):
                               data_to_save[num_col] = None
                               errors.append(f"Row {index + 1}: Invalid numeric data for {num_col} on code {code}: {val}")
                               print(errors[-1])

                # --- Debug Print --- #
                print(f"--- Row {index + 1} (Code: {code}) - Data to Save: {data_to_save}")
                # ----------------- #

                if property_obj:
                    # Update existing property
                    for key, value in data_to_save.items():
                         setattr(property_obj, key, value)
                    updated_count += 1
                else:
                    # Insert new property
                    property_obj = Property(**data_to_save)
                    db.session.add(property_obj)
                    inserted_count += 1

            # --- Bulk Deletion --- #
            # Delete properties in the DB that are NOT in the uploaded CSV
            if uploaded_codes:
                 # Get codes currently in the database
                 current_db_codes = set([p.code for p in Property.query.with_entities(Property.code).all()])
                 # Find codes in the DB that are not in the uploaded file
                 codes_to_delete = list(current_db_codes - uploaded_codes)
                 if codes_to_delete:
                      # Bulk delete
                      deleted_count = Property.query.filter(Property.code.in_(codes_to_delete)).delete(synchronize_session='fetch')
                      print(f"Deleted {deleted_count} properties not found in the uploaded CSV.")
                 else:
                      deleted_count = 0
                      print("No properties to delete from the database based on the uploaded CSV.")
            else:
                 # If uploaded CSV had no valid codes, perhaps delete all existing or handle as an error
                 # For now, print a warning and don't delete everything accidentally
                 print("Warning: Uploaded CSV contained no valid codes. Skipping bulk deletion.")
                 deleted_count = 0

            db.session.commit()

            return jsonify({
                'message': 'File uploaded and database updated successfully!',
                'geocoded_count': geocoded_count,
                'updated_count': updated_count,
                'inserted_count': inserted_count,
                'deleted_count': deleted_count,
                'errors': errors
            }), 200

        except pd.errors.EmptyDataError:
            db.session.rollback()
            return jsonify({'error': 'Uploaded CSV file is empty'}), 400
        except Exception as e:
            db.session.rollback()
            print(f"Error processing uploaded file and updating database: {e}")
            return jsonify({'error': f'Error processing file and updating database: {e}'}), 500
    else:
        return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

if __name__ == '__main__':
    # Get the port from the environment variable, default to 8080 for local development
    port = int(os.environ.get('PORT', 8080))
    # Run the app on all interfaces and the specified port
    # In production, you would typically use a WSGI server like Gunicorn instead of debug=True
    app.run(host='0.0.0.0', port=port, debug=True) 