import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a base class for declarative table definitions
Base = declarative_base()

# Function to create the database engine
def get_db_engine(db_uri: str):
    """Creates and returns a SQLAlchemy engine."""
    try:
        engine = create_engine(db_uri)
        logging.info("Database engine created successfully.")
        return engine
    except Exception as e:
        logging.error(f"Error creating database engine: {e}", exc_info=True)
        raise

# Function to create a session factory
def get_db_session_maker(engine: any):  # Using 'any' for simplicity; specify engine type if needed
    """Creates and returns a SQLAlchemy session maker."""
    try:
        session_maker = sessionmaker(bind=engine)
        logging.info("Database session maker created successfully.")
        return session_maker
    except Exception as e:
        logging.error(f"Error creating session maker: {e}", exc_info=True)
        raise

# Example usage (not recommended in this file for production)
if __name__ == "__main__":
    # Replace with your actual database URI
    db_uri = "postgresql://your_user:your_password@your_host:your_port/your_database"
    engine = get_db_engine(db_uri)
    Session = get_db_session_maker(engine)
    session = Session()

    try:
        # Example: Perform a simple query (replace with your actual table/model)
        # from .models import Patient  # Import your SQLAlchemy model
        # first_patient = session.query(Patient).first()
        # if first_patient:
        #     print(f"First patient: {first_patient.name}")
        # else:
        #     print("No patients found.")

        print("Database connection and setup successful (if no errors above).")

    except Exception as e:
        logging.error(f"Error during example usage: {e}", exc_info=True)
    finally:
        session.close() # Close the session