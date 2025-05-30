import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Date, Time, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

Base = declarative_base()
metadata = MetaData()  # Explicitly create MetaData


class Patient(Base):
    """Represents a patient in the database."""
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)  # Age can be nullable
    gender = Column(String(50), nullable=True)  # Gender can be nullable
    contact_info = Column(Text, nullable=True)  # Contact info can be nullable
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Patient(name='{self.name}', age={self.age}, gender='{self.gender}')>"


class Encounter(Base):
    """Represents a patient encounter in the database."""
    __tablename__ = "encounters"

    encounter_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id", ondelete="CASCADE"), nullable=False)
    encounter_date = Column(Date, nullable=False)
    encounter_time = Column(Time, nullable=True)  # Time can be nullable
    chief_complaint = Column(Text, nullable=True)  # Chief complaint can be nullable
    notes = Column(Text, nullable=True)  # Notes can be nullable
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)  # User ID can be nullable
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Encounter(patient_id={self.patient_id}, encounter_date='{self.encounter_date}')>"


class Test(Base):
    """Represents a medical test."""
    __tablename__ = "tests"

    test_id = Column(Integer, primary_key=True)
    encounter_id = Column(Integer, ForeignKey("encounters.encounter_id", ondelete="CASCADE"), nullable=False)
    test_type = Column(String(100), nullable=False)
    test_results = Column(Text, nullable=True)  # Test results can be nullable
    test_date = Column(Date, nullable=True)  # Test date can be nullable
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Test(test_type='{self.test_type}')>"


class Symptom(Base):
    """Represents a patient symptom."""
    __tablename__ = "symptoms"

    symptom_id = Column(Integer, primary_key=True)
    encounter_id = Column(Integer, ForeignKey("encounters.encounter_id", ondelete="CASCADE"), nullable=False)
    symptom_name = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=True)  # Severity can be nullable
    notes = Column(Text, nullable=True)  # Notes can be nullable
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Symptom(symptom_name='{self.symptom_name}', severity='{self.severity}')>"


class User(Base):
    """Represents a user of the system (medical personnel)."""
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Store hashed passwords!
    role = Column(String(50), nullable=True)  # Role can be nullable
    full_name = Column(String(255), nullable=True)  # Full name can be nullable
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


def create_schema(engine):
    """
    Creates the database schema in the PostgreSQL database.

    Args:
        engine: A SQLAlchemy engine instance connected to the database.
    """

    try:
        Base.metadata.create_all(engine)
        logging.info("Database schema created successfully.")
    except Exception as e:
        logging.error(f"Error creating database schema: {e}", exc_info=True)


if __name__ == "__main__":
    from sqlalchemy import create_engine

    # Replace with your actual database connection string
    engine = create_engine("postgresql://your_user:your_password@your_host:your_port/your_database")

    create_schema(engine)