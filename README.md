# Foreclosure Map

## Project Description

This project is a web application built with Flask that allows users to visualize foreclosure property listings on an interactive map. The property data, including location details, price, and other relevant information, is loaded from a CSV file and stored in a PostgreSQL database for persistence and efficient retrieval. The application provides a public interface displaying the map with markers for each property. Users can view detailed information about a property by clicking on its marker, which opens a popup. Additionally, there is a protected admin interface that allows authorized users to upload new CSV files to update the property listings in the database. The application is designed to be deployable on platforms like Railway, utilizing environment variables for configuration management.

The primary goal of this application is to provide a simple yet effective way to display and manage a dataset of geocoded properties, making it easy for potential buyers or interested parties to browse listings visually on a map.

## File Breakdown

Here's a description of the main files in this project:

*   **`app.py`**: This is the core Python Flask application file. It contains the server-side logic for the web application. Key components include:
    *   Flask application setup and configuration, including setting up the secret key and database URI using environment variables.
    *   Integration with `python-dotenv` for loading environment variables from a `.env` file during local development.
    *   Database setup and interaction using SQLAlchemy, defining the `Property` model to represent the structure of the property data stored in the PostgreSQL database.
    *   Routes for handling incoming HTTP requests:
        *   `/`: Renders the main `index.html` template, which displays the map.
        *   `/api/properties`: An API endpoint that fetches property data from the database, converts it into a JSON format suitable for the frontend, and returns it.
        *   `/admin`: A protected route (requiring login) that renders the `admin.html` template for uploading CSV files.
        *   `/login`: Handles the login logic for the admin interface.
        *   `/logout`: Handles the logout logic.
        *   `/upload`: Handles POST requests for uploading new CSV files. This function reads the uploaded CSV, processes the data (including ensuring data types and handling potential missing values), performs geocoding if necessary (though this part of the logic might be simplified now, it was a consideration), updates existing properties or inserts new ones based on a unique code, and deletes properties from the database that are no longer present in the uploaded CSV. It includes robust error handling for file processing and database operations.
    *   Includes a geocoding function (`geocode_address_google`) that interacts with the Google Maps Geocoding API to get latitude and longitude for addresses, with basic rate limiting.
    *   Includes a function (`load_initial_data_to_db`) to load data from a local `Bank_Listings.csv` file into the database when the application starts, but only if the database table is empty. This is useful for initial setup.
    *   Contains the `to_dict` method in the `Property` model to easily convert database objects to dictionaries for JSON serialization, with handling for `None` values.

*   **`templates/index.html`**: This is the HTML template for the main map view. It includes:
    *   The basic HTML5 structure.
    *   Links to external libraries like Leaflet (for the interactive map) and Bootstrap (for basic styling and potentially the modal, although the modal was later replaced by Leaflet popups).
    *   CSS for styling the map and filter elements.
    *   JavaScript code that initializes the Leaflet map, fetches property data from the `/api/properties` endpoint, adds markers to the map for each property with valid coordinates, and binds a popup to each marker. The popup displays detailed property information fetched from the backend, including the property code, address, price, area details, sales officer, and an image if available.
    *   Includes input fields and a button for potential filtering functionality based on location, property type, and price range, although the filtering logic is implemented in the `updateMarkers` JavaScript function on the frontend.

*   **`templates/admin.html`**: This HTML template provides the interface for the admin user to upload a CSV file. It contains a simple form with a file input field and a submit button that sends the CSV to the `/upload` endpoint.

*   **`templates/login.html`**: This HTML template provides a basic login form for accessing the `/admin` route. It takes a username and password as input.

*   **`requirements.txt`**: This file lists the Python packages required by the project (e.g., Flask, pandas, Flask-SQLAlchemy, psycopg2, python-dotenv, requests). It is used by pip to install the project's dependencies, crucial for setting up virtual environments and for deployment platforms.

*   **`.gitignore`**: This file specifies intentionally untracked files and directories that Git should ignore. It includes entries for the Python virtual environment (`venv/`), cache directories (`__pycache__/`), local environment file (`.env`), and potentially generated files like geocode caches (`geocode_cache.csv`, `geocode_cache_google.csv`). This prevents sensitive information and build artifacts from being committed to the Git repository.

*   **`Procfile`**: This file is used by platforms like Railway to specify the command needed to start the application's web server. It typically tells the platform to run a WSGI server (like Gunicorn) with your Flask application.

*   **`.env`**: This file (not committed to Git due to `.gitignore`) is used for storing environment-specific variables locally, such as `DATABASE_URL`, `SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, and `GOOGLE_MAPS_API_KEY`. `python-dotenv` reads this file and loads these variables into the environment when the application starts locally.

*   **`Bank_Listings.csv`**: The default CSV file containing the initial property data. While the application primarily uses the database after the initial load or subsequent uploads, this file serves as the initial data source.

## Design Choices and Debates

Several design choices were made during the development of this application:

*   **Flask vs. Django/Other Frameworks:** Flask was chosen for its simplicity and lightweight nature. For a relatively small application focused on a specific task like displaying data on a map with a simple admin interface, Flask provides enough functionality without the overhead of a full-featured framework like Django. The debate here often revolves around whether the project's potential future complexity warrants starting with a more opinionated and feature-rich framework. For this project's scope, Flask was deemed appropriate.

*   **SQLAlchemy for Database Interaction:** SQLAlchemy was chosen as the Object-Relational Mapper (ORM) to interact with the PostgreSQL database. An ORM simplifies database operations by allowing developers to work with Python objects rather than writing raw SQL queries. This makes the code cleaner, more maintainable, and less prone to SQL injection vulnerabilities compared to manual SQL string formatting. The alternative would be to use a lower-level database adapter like `psycopg2` directly, which would require writing SQL for every database operation.

*   **PostgreSQL Database:** PostgreSQL was selected as the database system due to its robustness, reliability, and suitability for handling structured data like property listings. Railway's easy integration with PostgreSQL was also a factor. Other choices could include SQLite (simpler, file-based, good for small projects but less robust for concurrent access) or MySQL.

*   **Frontend Approach (Leaflet + Vanilla JS/Bootstrap):** The frontend uses Leaflet for the map functionality and a combination of vanilla JavaScript and Bootstrap for the UI elements and modal/popup display. A full frontend framework like React, Vue, or Angular was not used to keep the project simpler and avoid the complexity of a separate frontend build process and state management for this relatively straightforward interface. This choice is a trade-off between development speed for simple UIs and scalability/maintainability for more complex interactive frontends.

*   **Data Persistence (Database vs. File):** Initially, data might have been loaded directly from the CSV for each request or stored in memory. However, moving to a database (PostgreSQL with SQLAlchemy) was a crucial design decision for persistence (data survives server restarts), concurrent access (multiple users/processes can access the data reliably), and enabling more complex querying and filtering on the backend if needed in the future. Storing data only in memory or directly from a CSV on each request would not be scalable or persistent.

*   **CSV Upload for Updates:** The admin interface allows updating listings by uploading a new CSV. The logic is implemented to effectively replace the existing dataset with the new one (deleting properties not in the new CSV and updating/inserting others). This is a simple and convenient update mechanism for this type of application. An alternative could be providing individual CRUD (Create, Read, Update, Delete) interfaces for properties, which would offer more fine-grained control but add significant complexity to the admin UI and backend logic.

*   **Geocoding Strategy:** Using the Google Maps Geocoding API provides accurate geocoding. The decision to initially geocode during the CSV upload process and store coordinates in the database avoids needing to geocode on every map load. Handling API keys securely via environment variables was essential. The exploration of caching geocoded results locally (using cache files that were later added to `.gitignore`) was a consideration to reduce API calls and speed up processing, demonstrating an iterative design process.

*   **Authentication:** A simple username/password login with Flask sessions was implemented for the admin area. This is suitable for a basic administrative interface. For applications requiring more robust security or user roles, more complex authentication systems (like OAuth, Flask-Login with database-backed users, etc.) would be necessary. The debate here is about balancing required security levels with development effort.

*   **Environment Variable Management:** Utilizing `python-dotenv` locally and relying on the deployment platform's (Railway) environment variable injection is a standard and secure practice for managing configuration and secrets outside of the codebase. Hardcoding sensitive information directly in the code would be insecure and make deployment across different environments difficult.

These design choices reflect a focus on building a functional application with a clear purpose, prioritizing simplicity and using appropriate tools for the task while being mindful of security and deployability.