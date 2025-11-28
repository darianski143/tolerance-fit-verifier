# Tolerance Fit Verifier

This web application calculates and verifies fits according to the ISO 286 standard for the dimension range [20 mm, 50 mm].

## Features

1.  **Fit Type Verification:** Determines if the fit is Clearance, Transition, or Interference (Press).
2.  **System Identification:** Determines if it is a Hole Basis or Shaft Basis system.
3.  **Preferred Fit Verification:** Checks if the entered fit is in the list of standard preferred fits.
4.  **Suggestions:** If the fit is not preferred, suggests a standard alternative.

## How to Run

### Requirements
*   Python 3.x installed

### Steps

1.  Open a terminal in this folder.
2.  Install dependencies (Flask):
    ```bash
    pip install -r requirements.txt
    ```
3.  Navigate to the application folder:
    ```bash
    cd app
    ```
4.  Start the server:
    ```bash
    python app.py
    ```
5.  Open your browser at the displayed address (usually `http://127.0.0.1:5000`).

## Project Structure

*   `app/app.py`: Flask web server.
*   `app/logic.py`: Engineering calculation logic and data tables (simplified for the 20-50mm range).
*   `app/templates/index.html`: User interface.
