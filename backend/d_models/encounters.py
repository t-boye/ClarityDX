import logging
from typing import Optional

from sqlalchemy import Column, Integer, Date, Time, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Encounter(Base):
    """
    Represents a patient encounter in the database.
    """

    __tablename__ = "encounters"

    encounter_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    encounter_date = Column(Date, nullable=False)
    encounter_time = Column(Time)
    chief_complaint = Column(String)
    notes = Column(Text)
    user_id = Column(Integer, ForeignKey("users.user_id"))  # User who conducted the encounter
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to Patient (if using SQLAlchemy ORM for related operations)
    patient = relationship("Patient", backref="encounters")

    def __repr__(self):
        return f"<Encounter(patient_id={self.patient_id}, encounter_date='{self.encounter_date}')>"


# --- Example Usage (Outside of a Flask request context) ---
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Replace with your actual database connection string
    engine = create_engine("postgresql://your_user:your_password@your_host:your_port/your_database")
    Base.metadata.create_all(engine)  # Create the table (if it doesn't exist)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Assuming you have a Patient object (e.g., from a previous operation)
        # For demonstration, let's create one (you'd normally fetch it)
        from d_models.patients import Patient  # Import Patient model
        new_patient = Patient(name="Alice Smith", age=32, gender="Female")
        session.add(new_patient)
        session.commit()

        # Create a new encounter
        new_encounter = Encounter(
            patient_id=new_patient.patient_id,  # Use the patient's ID
            encounter_date="2025-04-01",
            encounter_time="10:00:00",
            chief_complaint="Fever and headache",
            notes="Patient reports fever and headache for 3 days."
        )
        session.add(new_encounter)
        session.commit()
        logging.info(f"Created encounter: {new_encounter}")

        # Fetch encounters for a patient
        patient_encounters = session.query(Encounter).filter_by(patient_id=new_patient.patient_id).all()
        if patient_encounters:
            print("Encounters for Alice Smith:")
            for enc in patient_encounters:
                print(f"  - {enc}")
        else:
            print("No encounters found for this patient.")

        # Update an encounter
        if patient_encounters:
            first_encounter = patient_encounters[0]
            first_encounter.notes = "Patient's condition improving."
            session.commit()
            logging.info(f"Updated encounter: {first_encounter}")

        # Delete an encounter (demonstration - usually you wouldn't delete)
        if patient_encounters:
            session.delete(patient_encounters[0])
            session.commit()
            logging.info(f"Deleted encounter.")

    except Exception as e:
        session.rollback()
        logging.error(f"Error during example usage: {e}", exc_info=True)
    finally:
        session.close()