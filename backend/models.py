# models.py
from datetime import datetime
import random
import string
from extensions import db

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

class PatientNotFoundError(Exception):
    """Custom exception for when a patient is not found."""
    pass

class EncounterNotFoundError(Exception):
    """Custom exception for when an encounter is not found."""
    pass

class RecordNotFoundError(Exception):
    """Custom exception for when a record is not found."""
    pass

def generate_unique_patient_code(prefix: str = "TSys") -> str:
    """Generates a unique patient code."""
    return f"{prefix}-{random.randint(100000, 999999)}"

class Patient(db.Model):
    __tablename__ = 'patients' # Explicitly define table name if different from class name

    patient_id = db.Column(db.Integer, primary_key=True)
    unique_patient_code = db.Column(db.String(50), unique=True, nullable=False, default=generate_unique_patient_code)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    contact_info = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define relationship with Encounter
    encounters = db.relationship('Encounter', backref='patient', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.patient_id}: {self.name} ({self.unique_patient_code})>"

    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'unique_patient_code': self.unique_patient_code,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Encounter(db.Model):
    __tablename__ = 'encounters'

    encounter_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    encounter_date = db.Column(db.Date, nullable=False) # Store as Date type
    encounter_time = db.Column(db.Time) # Store as Time type
    chief_complaint = db.Column(db.Text)
    notes = db.Column(db.Text)
    user_id = db.Column(db.Integer) # Assuming a users table, but not defined here yet
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define relationship with Record
    records = db.relationship('Record', backref='encounter', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Encounter {self.encounter_id} for Patient {self.patient_id} on {self.encounter_date}>"

    def to_dict(self):
        return {
            'encounter_id': self.encounter_id,
            'patient_id': self.patient_id,
            'encounter_date': self.encounter_date.isoformat() if self.encounter_date else None,
            'encounter_time': self.encounter_time.isoformat() if self.encounter_time else None,
            'chief_complaint': self.chief_complaint,
            'notes': self.notes,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Record(db.Model):
    __tablename__ = 'records'

    record_id = db.Column(db.Integer, primary_key=True)
    encounter_id = db.Column(db.Integer, db.ForeignKey('encounters.encounter_id'), nullable=False)
    record_date = db.Column(db.Date, nullable=False) # Store as Date type
    details = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer) # Assuming a users table
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Record {self.record_id} for Encounter {self.encounter_id} on {self.record_date}>"

    def to_dict(self):
        return {
            'record_id': self.record_id,
            'encounter_id': self.encounter_id,
            'record_date': self.record_date.isoformat() if self.record_date else None,
            'details': self.details,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }