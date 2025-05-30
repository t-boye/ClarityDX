import logging
from typing import Optional

from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Patient(Base):
    """
    Represents a patient in the database.
    """

    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    gender = Column(String(50))
    contact_info = Column(String)  # Changed TEXT to String for simplicity
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Patient(name='{self.name}', age={self.age}, gender='{self.gender}')>"


# --- Example Usage (Outside of a Flask request context) ---
if __name__ == "__main__":
    # This section is for basic testing/demonstration
    # You'll typically use an ORM setup with Flask-SQLAlchemy or similar
    # and not create engine/session directly in this file.

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Replace with your actual database connection string
    engine = create_engine("postgresql://your_user:your_password@your_host:your_port/your_database")
    Base.metadata.create_all(engine)  # Create the table (if it doesn't exist)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create a new patient
        new_patient = Patient(name="John Doe", age=45, gender="Male", contact_info="john.doe@example.com")
        session.add(new_patient)
        session.commit()
        logging.info(f"Created patient: {new_patient}")

        # Fetch a patient
        fetched_patient = session.query(Patient).filter_by(name="John Doe").first()
        if fetched_patient:
            print(f"Fetched patient: {fetched_patient}")
            fetched_patient.age = 46  # Update age
            session.commit()
            logging.info(f"Updated patient: {fetched_patient}")
        else:
            print("Patient not found.")

        # Delete a patient
        if fetched_patient:
            session.delete(fetched_patient)
            session.commit()
            logging.info(f"Deleted patient: {fetched_patient}")

    except Exception as e:
        session.rollback()
        logging.error(f"Error during example usage: {e}", exc_info=True)
    finally:
        session.close()