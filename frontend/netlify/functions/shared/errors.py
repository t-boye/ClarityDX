# errors.py

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