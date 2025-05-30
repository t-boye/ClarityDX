import logging
from waitress import serve
from app import app  # Import your Flask app instance from app.py

# Configure logging
logging.basicConfig(level=logging.INFO,
                  format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("Starting Waitress server...")  # Log start message
    try:
        serve(app, host='0.0.0.0', port=8000)
        logging.info("Waitress server started successfully.")  # Log success
    except Exception as e:
        logging.error(f"Error starting Waitress server: {e}")  # Log error