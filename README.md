# Foreclosure Map

## Project Description

This project is a web application built with Flask that allows users to visualize foreclosure property listings on an interactive map. Property data is loaded from a CSV file and stored in a PostgreSQL database, providing a persistent and searchable source of information. The application features a public interface with a map displaying markers for each geocoded property. Clicking a marker reveals a popup with detailed information about that listing. A separate, protected admin interface facilitates securely uploading new CSV files to update the database, adding new properties, updating existing ones, and removing listings not present in the new file.

**Live Demo:** You can access the live deployed application here: [https://foreclosure-map-production.up.railway.app/](https://foreclosure-map-production.up.railway.app/)

## Application Logic and Data Flow

The application follows a clear data flow:

1.  **Data Source:** Property listings are initially provided in a CSV file (`Bank_Listings.csv`).
2.  **Initial Load/Upload:**
    *   When the application starts and the database is empty, the `load_initial_data_to_db` function reads the `Bank_Listings.csv` file and populates the database.
    *   Administrators can upload a new CSV file via the `/upload` endpoint. The `upload_csv` function reads this file.
3.  **Data Processing (during Upload/Initial Load):** The loaded CSV data is processed row by row. Key steps include:
    *   Extracting data fields like Code, Category, Address, Price, Area, etc.
    *   Handling potential missing or `NaN` values by converting them to `None`.
    *   Performing geocoding for properties that are missing Latitude and Longitude coordinates using the Google Maps Geocoding API.
    *   Preparing the data to match the `Property` model structure.
4.  **Database Interaction:** Processed data is used to interact with the PostgreSQL database via SQLAlchemy:
    *   Existing properties (matched by 'Code') are updated.
    *   New properties are inserted.
    *   Properties in the database that are *not* in the uploaded CSV are deleted, ensuring the database reflects the latest uploaded data.
5.  **Frontend Data Fetching:** The public map interface (`index.html`) makes an asynchronous request to the `/api/properties` endpoint.
6.  **Backend Data Retrieval:** The `/api/properties` route queries the database using SQLAlchemy to fetch all stored property listings.
7.  **Data Serialization:** The fetched database objects are converted into a list of dictionaries using the `to_dict` method, which formats the data (e.g., handles `None` values, formats price). This list is then returned as a JSON response.
8.  **Frontend Map Display:** The JavaScript code in `index.html` receives the JSON data. For each property with valid latitude and longitude, it creates a marker on the Leaflet map and binds a popup containing the property's details.

## Endpoints

The application exposes the following endpoints:

*   **`/` (GET):** Renders the main map page (`index.html`). This is the public entry point of the application.
*   **`/api/properties` (GET):** Returns a JSON array of all property listings stored in the database. This endpoint is consumed by the frontend JavaScript to populate the map.
*   **`/admin` (GET):** Renders the admin file upload page (`admin.html`). This route is protected and requires authentication.
*   **`/login` (GET, POST):** Renders the login form (GET) and handles the submission of login credentials (POST). Successful login sets a session variable for authentication.
*   **`/logout` (GET):** Clears the session and redirects the user to the home page, effectively logging them out.
*   **`/upload` (POST):** Accepts a CSV file upload from the admin interface. Processes the file, updates the database with the new data (inserting, updating, and deleting as necessary), and returns a JSON response indicating the status and any errors.

## User Flow

**Public User Flow:**

1.  A user navigates to the application's root URL (`/`).
2.  The server renders the `index.html` page containing the map.
3.  The frontend JavaScript automatically fetches property data from `/api/properties`.
4.  Properties with coordinates are displayed as markers on the map.
5.  The user can interact with the map (pan, zoom).
6.  Clicking on a marker opens a popup displaying detailed information about the property.
7.  (Optional) Users can use the filter inputs (location, type, price) to narrow down the properties displayed on the map.

**Administrator User Flow:**

1.  An administrator navigates to the `/admin` route.
2.  If not logged in, they are redirected to the `/login` page.
3.  On the `/login` page, the administrator enters their username and password and submits the form.
4.  If credentials are correct, the session is set, and the administrator is redirected to the `/admin` page.
5.  On the `/admin` page, the administrator uses the file upload form to select and submit a new CSV file containing updated property listings.
6.  The `/upload` endpoint processes the CSV, updates the database, and returns a result.
7.  The administrator can log out by navigating to the `/logout` route.

## Key Technologies and Design Choices

*   **Flask:** Chosen as the web framework for its lightweight nature and flexibility. It provides the essential tools for routing HTTP requests, managing templates, and handling web application logic without imposing rigid structures, which was suitable for the project's scope.

*   **PostgreSQL & SQLAlchemy:** PostgreSQL was selected for its robust and reliable nature as a relational database, well-suited for structured data like property listings. SQLAlchemy was chosen as the ORM to provide an expressive Python interface for database operations. Using an ORM simplifies interactions compared to writing raw SQL, enhances code readability, and reduces the risk of SQL injection.

*   **Leaflet:** Selected as the JavaScript library for creating interactive maps. Leaflet is lightweight, mobile-friendly, and easy to use, providing all the necessary features for displaying map tiles, adding markers, and handling marker click events for popups.

*   **pandas:** Used for reading and processing data from CSV files in the Flask backend. pandas provides powerful and efficient data manipulation capabilities, making it straightforward to read CSV data into DataFrames, handle missing values (`NaN`), and iterate through rows.

*   **Google Maps Geocoding API:** Integrated to convert property addresses into geographical coordinates (Latitude and Longitude). This was necessary as the initial CSV might not contain coordinates for all listings. The API is called during the CSV upload process for properties missing coordinates. The API key is securely managed using environment variables.

*   **python-dotenv:** Used to load environment variables from a `.env` file during local development. This allows sensitive information like the database URL, secret key, and API keys to be stored outside the codebase, which is crucial for security and managing configuration across different environments (local vs. deployment).

*   **Environment Variables:** A fundamental design choice for managing configuration and secrets. Using environment variables ensures that sensitive data is not hardcoded into the application and allows for easy configuration changes between development and production environments like Railway.
