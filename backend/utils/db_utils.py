import psycopg2
import psycopg2.pool
import psycopg2.extras
import logging
import os
from typing import List, Optional, Dict, Any

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global connection pool
pg_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None


class DatabaseError(Exception):
    """Base class for database-related exceptions in this application."""
    pass


class PatientNotFoundError(DatabaseError):
    """Exception raised when a patient is not found."""
    pass


class EncounterNotFoundError(DatabaseError):
    """Exception raised when an encounter is not found."""
    pass


class RecordNotFoundError(DatabaseError):
    """Exception raised when a record is not found."""
    pass


def get_db_pool() -> psycopg2.pool.SimpleConnectionPool:
    """Initializes and returns the global PostgreSQL connection pool."""
    global pg_pool
    if pg_pool is None:
        try:
            db_name = os.environ.get("DB_NAME")
            db_user = os.environ.get("DB_USER")
            db_password = os.environ.get("DB_PASSWORD")
            db_host = os.environ.get("DB_HOST")
            db_port = os.environ.get("DB_PORT", "5432")

            if not all([db_name, db_user, db_password, db_host]):
                raise ValueError("Missing database environment variables")

            pg_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,  # Adjust as needed
                maxconn=10,  # Adjust as needed
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            logging.info("Database connection pool initialized.")
        except ValueError as e:
            logging.error(f"Error initializing database pool: {e}")
            raise
        except psycopg2.Error as e:
            logging.error(f"Error connecting to the database: {e}")
            raise
    return pg_pool


def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """Gets a connection from the pool."""
    pool = get_db_pool()
    if pool:
        try:
            conn = pool.getconn()
            return conn
        except psycopg2.OperationalError as e:  # Catch specific connection errors
            logging.error(f"Error getting connection from pool: {e}")
            return None
        except psycopg2.pool.PoolError as e:  # Catch pool-specific errors
            logging.error(f"Error getting connection from pool: {e}")
            return None
    return None


def put_db_connection(conn: psycopg2.extensions.connection) -> None:
    """Puts a connection back into the pool."""
    pool = get_db_pool()
    if pool and conn:
        pool.putconn(conn)


def close_db_pool() -> None:
    """Closes the connection pool."""
    global pg_pool
    if pg_pool:
        pg_pool.closeall()
        pg_pool = None
        logging.info("Database connection pool closed.")


# --- Patient Operations ---

import random
import string

def generate_unique_patient_code(prefix: str = "TSys") -> str:
    return f"{prefix}-{random.randint(1000, 9999)}"

def create_patient(conn: psycopg2.extensions.connection, name: str, age: Optional[int] = None,
                   gender: Optional[str] = None, contact_info: Optional[str] = None,
                   unique_patient_code: Optional[str] = None) -> int:
    """
    Creates a new patient record in the database.

    Args:
        conn: The database connection.
        name: The patient's name (required).
        age: The patient's age (optional).
        gender: The patient's gender (optional).
        contact_info: The patient's contact information (optional).
        unique_patient_code: Optional manually-supplied patient code (if not provided, it will be auto-generated).

    Returns:
        The patient_id of the newly created patient.

    Raises:
        DatabaseError: If there's a database-related error.
    """
    cur = None
    try:
        if not unique_patient_code:
            unique_patient_code = generate_unique_patient_code()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO patients (unique_patient_code, name, age, gender, contact_info)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING patient_id
        """, (unique_patient_code, name, age, gender, contact_info))
        patient_id = cur.fetchone()[0]
        conn.commit()
        logging.info(f"Patient created with ID: {patient_id}, Code: {unique_patient_code}")
        return patient_id
    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        raise DatabaseError(f"Duplicate unique_patient_code: {e}") from e
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error creating patient: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error creating patient: {e}") from e
    finally:
        if cur:
            cur.close()




def fetch_patient_by_id(conn: psycopg2.extensions.connection, patient_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches patient data by patient ID.

    Args:
        conn: The database connection.
        patient_id: The ID of the patient to fetch.

    Returns:
        A dictionary containing the patient's data, or None if not found.

    Raises:
        DatabaseError: If there's a database-related error.
        PatientNotFoundError: If the patient with the given ID is not found.
    """
    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT patient_id, unique_patient_code, name, age, gender, contact_info, created_at, updated_at
            FROM patients WHERE patient_id = %s
        """, (patient_id,))
        patient = cur.fetchone()
        if patient:
            logging.info(f"Patient fetched: {patient}")
            return dict(patient)
        else:
            raise PatientNotFoundError(f"Patient with ID {patient_id} not found")
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error fetching patient: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error fetching patient: {e}") from e
    finally:
        if cur:
            cur.close()



def fetch_all_patients(conn: psycopg2.extensions.connection) -> List[Dict[str, Any]]:
    """
    Fetches all patient records.

    Args:
        conn: The database connection.

    Returns:
        A list of dictionaries, where each dictionary represents a patient.

    Raises:
        DatabaseError: If there's a database-related error.
    """
    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT patient_id, unique_patient_code, name, age, gender, contact_info, created_at, updated_at
            FROM patients
        """)
        patients = cur.fetchall()
        logging.info(f"Fetched {len(patients)} patients.")
        return [dict(p) for p in patients]
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error fetching all patients: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error fetching all patients: {e}") from e
    finally:
        if cur:
            cur.close()



def update_patient(conn: psycopg2.extensions.connection, patient_id: int, name: Optional[str] = None,
                   age: Optional[int] = None, gender: Optional[str] = None,
                   contact_info: Optional[str] = None) -> int:
    """
    Updates patient data.

    Args:
        conn: The database connection.
        patient_id: The ID of the patient to update.
        name: The new name (optional).
        age: The new age (optional).
        gender: The new gender (optional).
        contact_info: The new contact information (optional).

    Returns:
        The number of rows affected by the update.

    Raises:
        DatabaseError: If there's a database-related error.
        PatientNotFoundError: If the patient with the given ID is not found.
    """
    cur = None
    try:
        updates = []
        values = []
        if name is not None:
            updates.append("name = %s")
            values.append(name)
        if age is not None:
            updates.append("age = %s")
            values.append(age)
        if gender is not None:
            updates.append("gender = %s")
            values.append(gender)
        if contact_info is not None:
            updates.append("contact_info = %s")
            values.append(contact_info)

        if updates:
            set_clause = ", ".join(updates)
            sql = f"UPDATE patients SET {set_clause} WHERE patient_id = %s"
            values.append(patient_id)

            cur = conn.cursor()
            cur.execute(sql, tuple(values))
            rows_affected = cur.rowcount
            conn.commit()
            if rows_affected > 0:
                logging.info(f"Patient with ID {patient_id} updated.")
                return rows_affected
            else:
                raise PatientNotFoundError(f"Patient with ID {patient_id} not found for update")
        else:
            logging.warning("No updates provided for patient.")
            return 0
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error updating patient: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error updating patient: {e}") from e
    finally:
        if cur:
            cur.close()


def delete_patient(conn: psycopg2.extensions.connection, patient_id: int) -> int:
    """
    Deletes a patient record.

    Args:
        conn: The database connection.
        patient_id: The ID of the patient to delete.

    Returns:
        The number of rows affected by the deletion (1 if successful, 0 if not found).

    Raises:
        DatabaseError: If there's a database-related error.
        PatientNotFoundError: If the patient with the given ID is not found.
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM patients WHERE patient_id = %s", (patient_id,))
        rows_affected = cur.rowcount
        conn.commit()
        if rows_affected > 0:
            logging.info(f"Patient with ID {patient_id} deleted.")
            return rows_affected
        else:
            raise PatientNotFoundError(f"Patient with ID {patient_id} not found for deletion")
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error deleting patient: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error deleting patient: {e}") from e
    finally:
        if cur:
            cur.close()


# --- Encounter Operations ---

def create_encounter(
        conn: psycopg2.extensions.connection,
        patient_id: int,
        encounter_date: str,
        encounter_time: Optional[str] = None,
        chief_complaint: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None,
) -> int:
    """
    Creates a new encounter record.

    Args:
        conn: The database connection.
        patient_id: The ID of the patient for the encounter.
        encounter_date: The date of the encounter (YYYY-MM-DD).
        encounter_time: The time of the encounter (optional).
        chief_complaint: The patient's main complaint (optional).
        notes: Additional notes about the encounter (optional).
        user_id: The ID of the user who conducted the encounter (optional).

    Returns:
        The ID of the newly created encounter.

    Raises:
        DatabaseError: If there's a database-related error.
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO encounters (patient_id, encounter_date, encounter_time, chief_complaint, notes, user_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING encounter_id",
            (patient_id, encounter_date, encounter_time, chief_complaint, notes, user_id)
        )
        encounter_id = cur.fetchone()[0]
        conn.commit()
        logging.info(f"Encounter created with ID: {encounter_id}")
        return encounter_id
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error creating encounter: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error creating encounter: {e}") from e
    finally:
        if cur:
            cur.close()


def fetch_encounters_by_patient(conn: psycopg2.extensions.connection, patient_id: int) -> List[Dict[str, Any]]:
    """
    Fetches all encounter records for a given patient.

    Args:
        conn: The database connection.
        patient_id: The ID of the patient.

    Returns:
        A list of dictionaries, where each dictionary represents an encounter.

    Raises:
        DatabaseError: If there's a database-related error.
    """
    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT encounter_id, encounter_date, encounter_time, chief_complaint, notes, user_id FROM encounters WHERE patient_id = %s ORDER BY encounter_date DESC, encounter_time DESC",
            (patient_id,)
        )
        encounters = cur.fetchall()
        logging.info(f"Fetched {len(encounters)} encounters for patient ID: {patient_id}")
        return encounters
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error fetching encounters: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error fetching encounters: {e}") from e
    finally:
        if cur:
            cur.close()


def update_encounter(
        conn: psycopg2.extensions.connection,
        encounter_id: int,
        encounter_date: Optional[str] = None,
        encounter_time: Optional[str] = None,
        chief_complaint: Optional[str] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None,
) -> int:
    """
    Updates an encounter record.

    Args:
        conn: The database connection.
        encounter_id: The ID of the encounter to update.
        encounter_date: The new encounter date (optional).
        encounter_time: The new encounter time (optional).
        chief_complaint: The new chief complaint (optional).
        notes: The new notes (optional).
        user_id: The new user ID (optional).

    Returns:
        The number of rows affected by the update.

    Raises:
        DatabaseError: If there's a database-related error.
        EncounterNotFoundError: If the encounter with the given ID is not found.
    """
    cur = None
    try:
        updates = []
        values = []
        if encounter_date is not None:
            updates.append("encounter_date = %s")
            values.append(encounter_date)
        if encounter_time is not None:
            updates.append("encounter_time = %s")
            values.append(encounter_time)
        if chief_complaint is not None:
            updates.append("chief_complaint = %s")
            values.append(chief_complaint)
        if notes is not None:
            updates.append("notes = %s")
            values.append(notes)
        if user_id is not None:
            updates.append("user_id = %s")
            values.append(user_id)

        if updates:
            set_clause = ", ".join(updates)
            sql = f"UPDATE encounters SET {set_clause} WHERE encounter_id = %s"
            values.append(encounter_id)

            cur = conn.cursor()
            cur.execute(sql, tuple(values))
            rows_affected = cur.rowcount
            conn.commit()
            if rows_affected > 0:
                logging.info(f"Encounter with ID {encounter_id} updated.")
                return rows_affected
            else:
                raise EncounterNotFoundError(f"Encounter with ID {encounter_id} not found for update")
        else:
            logging.warning("No updates provided for encounter.")
            return 0
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error updating encounter: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error updating encounter: {e}") from e
    finally:
        if cur:
            cur.close()


def delete_encounter(conn: psycopg2.extensions.connection, encounter_id: int) -> int:
    """
    Deletes an encounter record.

    Args:
        conn: The database connection.
        encounter_id: The ID of the encounter to delete.

    Returns:
        The number of rows affected by the deletion (1 if successful, 0 if not found).

    Raises:
        DatabaseError: If there's a database-related error.
        EncounterNotFoundError: If the encounter with the given ID is not found.
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM encounters WHERE encounter_id = %s", (encounter_id,))
        rows_affected = cur.rowcount
        conn.commit()
        if rows_affected > 0:
            logging.info(f"Encounter with ID {encounter_id} deleted.")
            return rows_affected
        else:
            raise EncounterNotFoundError(f"Encounter with ID {encounter_id} not found for deletion")
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error deleting encounter: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error deleting encounter: {e}") from e
    finally:
        if cur:
            cur.close()


def fetch_encounter_by_id(conn: psycopg2.extensions.connection, encounter_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a single encounter's details by ID.

    Args:
        conn: The database connection.
        encounter_id: The ID of the encounter to fetch.

    Returns:
        A dictionary containing the encounter's data, or None if not found.

    Raises:
        DatabaseError: If there's a database-related error.
        EncounterNotFoundError: If the encounter with the given ID is not found.
    """
    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT encounter_id, patient_id, encounter_date, encounter_time, chief_complaint, notes, user_id FROM encounters WHERE encounter_id = %s",
            (encounter_id,))
        encounter = cur.fetchone()
        if encounter:
            logging.info(f"Encounter fetched: {encounter}")
            return encounter
        else:
            raise EncounterNotFoundError(f"Encounter with ID {encounter_id} not found")
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error fetching encounter: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error fetching encounter: {e}") from e
    finally:
        if cur:
            cur.close()


# --- Record Operations ---

def create_record(
        conn: psycopg2.extensions.connection,
        encounter_id: int,
        record_date: str,
        details: str,
        user_id: Optional[int] = None,  # Added user_id
) -> int:
    """
    Creates a new record associated with an encounter.

    Args:
        conn: The database connection.
        encounter_id: The ID of the encounter to associate the record with.
        record_date: The date of the record (YYYY-MM-DD).
        details: The details of the record.
        user_id: The ID of the user creating the record (optional).

    Returns:
        The ID of the newly created record.

    Raises:
        DatabaseError: If there's a database-related error.
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO records (encounter_id, record_date, details, user_id) VALUES (%s, %s, %s, %s) RETURNING record_id",
            (encounter_id, record_date, details, user_id)
        )
        record_id = cur.fetchone()[0]
        conn.commit()
        logging.info(f"Record created with ID: {record_id} for encounter ID: {encounter_id}")
        return record_id
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error creating record: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error creating record: {e}") from e
    finally:
        if cur:
            cur.close()


def fetch_records_by_encounter(conn: psycopg2.extensions.connection, encounter_id: int) -> List[Dict[str, Any]]:
    """
    Fetches all records associated with a given encounter.

    Args:
        conn: The database connection.
        encounter_id: The ID of the encounter.

    Returns:
        A list of dictionaries, where each dictionary represents a record.

    Raises:
        DatabaseError: If there's a database-related error.
    """
    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "SELECT record_id, record_date, details, user_id FROM records WHERE encounter_id = %s ORDER BY record_date DESC",
            (encounter_id,)
        )
        records = cur.fetchall()
        logging.info(f"Fetched {len(records)} records for encounter ID: {encounter_id}")
        return records
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error fetching records: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error fetching records: {e}") from e
    finally:
        if cur:
            cur.close()


def fetch_record_by_id(conn: psycopg2.extensions.connection, record_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a single record's details by ID.

    Args:
        conn: The database connection.
        record_id: The ID of the record to fetch.

    Returns:
        A dictionary containing the record's data, or None if not found.

    Raises:
        DatabaseError: If there's a database-related error.
        RecordNotFoundError: If the record with the given ID is not found.
    """
    cur = None
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT record_id, encounter_id, record_date, details, user_id FROM records WHERE record_id = %s",
                    (record_id,))
        record = cur.fetchone()
        if record:
            logging.info(f"Record fetched: {record}")
            return record
        else:
            raise RecordNotFoundError(f"Record with ID {record_id} not found")
    except psycopg2.Error as e:
        raise DatabaseError(f"Database error fetching record: {e}") from e
    except Exception as e:
        raise DatabaseError(f"Unexpected error fetching record: {e}") from e
    finally:
        if cur:
            cur.close()


def update_record(
        conn: psycopg2.extensions.connection,
        record_id: int,
        record_date: Optional[str] = None,
        details: Optional[str] = None,
        user_id: Optional[int] = None,
) -> int:
    """
    Updates a record's details.

    Args:
        conn: The database connection.
        record_id: The ID of the record to update.
        record_date: The new record date (optional).
        details: The new details (optional).
        user_id: The ID of the user updating the record (optional).

    Returns:
        The number of rows affected by the update.

    Raises:
        DatabaseError: If there's a database-related error.
        RecordNotFoundError: If the record with the given ID is not found.
    """
    cur = None
    try:
        updates = []
        values = []
        if record_date is not None:
            updates.append("record_date = %s")
            values.append(record_date)
        if details is not None:
            updates.append("details = %s")
            values.append(details)
        if user_id is not None:
            updates.append("user_id = %s")
            values.append(user_id)

        if updates:
            set_clause = ", ".join(updates)
            sql = f"UPDATE records SET {set_clause} WHERE record_id = %s"
            values.append(record_id)

            cur = conn.cursor()
            cur.execute(sql, tuple(values))
            rows_affected = cur.rowcount
            conn.commit()
            if rows_affected > 0:
                logging.info(f"Record with ID {record_id} updated.")
                return rows_affected
            else:
                raise RecordNotFoundError(f"Record with ID {record_id} not found for update")
        else:
            logging.warning("No updates provided for record.")
            return 0
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error updating record: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error updating record: {e}") from e
    finally:
        if cur:
            cur.close()


def delete_record(conn: psycopg2.extensions.connection, record_id: int) -> int:
    """
    Deletes a record.

    Args:
        conn: The database connection.
        record_id: The ID of the record to delete.

    Returns:
        The number of rows affected by the deletion (1 if successful, 0 if not found).

    Raises:
        DatabaseError: If there's a database-related error.
        RecordNotFoundError: If the record with the given ID is not found.
    """
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM records WHERE record_id = %s", (record_id,))
        rows_affected = cur.rowcount
        conn.commit()
        if rows_affected > 0:
            logging.info(f"Record with ID {record_id} deleted.")
            return rows_affected
        else:
            raise RecordNotFoundError(f"Record with ID {record_id} not found for deletion")
    except psycopg2.Error as e:
        conn.rollback()
        raise DatabaseError(f"Database error deleting record: {e}") from e
    except Exception as e:
        conn.rollback()
        raise DatabaseError(f"Unexpected error deleting record: {e}") from e
    finally:
        if cur:
            cur.close()


if __name__ == "__main__":
    # Example Usage (for testing db_utils functions directly)
    import logging

    logging.basicConfig(level=logging.DEBUG)  # For more detailed output

    conn = None  # Initialize conn outside the try block
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to the database. Check your environment variables.")
        else:
            print("Connected to the database.")

            # Check database connection
            try:
                if is_db_active(conn):
                    print("Database is active and ready for operations.")
                else:
                    print("Database is inactive or not responding.")
            except Exception as e:
                print(f"Error checking database connection: {e}")

            patient_id = None  # Initialize patient_id
            encounter_id = None  # Initialize encounter_id
            record_id = None  # Initialize record_id

            # Example: Create a patient
            try:
                patient_id = create_patient(conn, name="Test Patient", age=40, gender="Other")
                if patient_id:
                    print(f"Created patient with ID: {patient_id}")
                else:
                    print("Failed to create patient.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Fetch patient by ID
            try:
                if patient_id:
                    patient = fetch_patient_by_id(conn, patient_id)
                    if patient:
                        print(f"Fetched patient: {patient}")
                    else:
                        print("Patient not found.")
                else:
                    print("No patient ID available to fetch.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except PatientNotFoundError as e:
                print(f"Patient not found error: {e}")

            # Example: Fetch all patients
            try:
                patients = fetch_all_patients(conn)
                if patients:
                    print("All Patients:")
                    for p in patients:
                        print(f"  - {p}")
                else:
                    print("No patients found.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Update a patient
            try:
                if patient_id:
                    updated = update_patient(conn, patient_id, name="Updated Patient Name")
                    if updated:
                        print("Patient updated successfully.")
                    else:
                        print("Patient not found or no updates applied.")
                else:
                    print("No patient ID available to update.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except PatientNotFoundError as e:
                print(f"Patient not found error: {e}")

            # Example: Delete a patient
            try:
                if patient_id:
                    deleted = delete_patient(conn, patient_id)
                    if deleted:
                        print("Patient deleted successfully.")
                    else:
                        print("Patient not found for deletion.")
                else:
                    print("No patient ID available to delete.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except PatientNotFoundError as e:
                print(f"Patient not found error: {e}")

            # Example: Create an encounter
            try:
                if patient_id:
                    encounter_id = create_encounter(conn, patient_id=patient_id, encounter_date="2025-04-05",
                                                    chief_complaint="Headache")
                    if encounter_id:
                        print(f"Created encounter with ID: {encounter_id}")
                    else:
                        print("Failed to create encounter.")
                else:
                    print("No patient ID available to create encounter.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Fetch encounters for a patient
            try:
                if patient_id:
                    encounters = fetch_encounters_by_patient(conn, patient_id)
                    if encounters:
                        print(f"Encounters for Patient {patient_id}:")
                        for enc in encounters:
                            print(f"  - {enc}")
                    else:
                        print("No encounters found for patient.")
                else:
                    print("No patient ID available to fetch encounters.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Update an encounter
            try:
                if encounter_id:
                    updated = update_encounter(conn, encounter_id, notes="Patient feeling better")
                    if updated:
                        print(f"Encounter {encounter_id} updated successfully.")
                    else:
                        print(f"Encounter {encounter_id} not found or no updates applied.")
                else:
                    print("No encounter ID available to update.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except EncounterNotFoundError as e:
                print(f"Encounter not found error: {e}")

            # Example: Delete an encounter
            try:
                if encounter_id:
                    deleted = delete_encounter(conn, encounter_id)
                    if deleted:
                        print(f"Encounter {encounter_id} deleted successfully.")
                    else:
                        print(f"Encounter {encounter_id} not found for deletion.")
                else:
                    print("No encounter ID available to delete.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except EncounterNotFoundError as e:
                print(f"Encounter not found error: {e}")

            # Example: Create a patient
            try:
                patient_id = create_patient(conn, name="Test Patient", age=40, gender="Other")
                if patient_id:
                    print(f"Created patient with ID: {patient_id}")
                else:
                    print("Failed to create patient.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Fetch patient by ID
            try:
                if patient_id:
                    patient = fetch_patient_by_id(conn, patient_id)
                    if patient:
                        print(f"Fetched patient: {patient}")
                    else:
                        print("Patient not found.")
                else:
                    print("No patient ID available to fetch.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except PatientNotFoundError as e:
                print(f"Patient not found error: {e}")

            # Example: Fetch all patients
            try:
                patients = fetch_all_patients(conn)
                if patients:
                    print("All Patients:")
                    for p in patients:
                        print(f"  - {p}")
                else:
                    print("No patients found.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Update a patient
            try:
                if patient_id:
                    updated = update_patient(conn, patient_id, name="Updated Patient Name")
                    if updated:
                        print("Patient updated successfully.")
                    else:
                        print("Patient not found or no updates applied.")
                else:
                    print("No patient ID available to update.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except PatientNotFoundError as e:
                print(f"Patient not found error: {e}")

            # Example: Delete a patient
            try:
                if patient_id:
                    deleted = delete_patient(conn, patient_id)
                    if deleted:
                        print("Patient deleted successfully.")
                    else:
                        print("Patient not found for deletion.")
                else:
                    print("No patient ID available to delete.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except PatientNotFoundError as e:
                print(f"Patient not found error: {e}")

            # Example: Create an encounter
            try:
                if patient_id:
                    encounter_id = create_encounter(conn, patient_id=patient_id, encounter_date="2025-04-05", chief_complaint="Headache")
                    if encounter_id:
                        print(f"Created encounter with ID: {encounter_id}")
                    else:
                        print("Failed to create encounter.")
                else:
                    print("No patient ID available to create encounter.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Fetch encounters for a patient
            try:
                if patient_id:
                    encounters = fetch_encounters_by_patient(conn, patient_id)
                    if encounters:
                        print(f"Encounters for Patient {patient_id}:")
                        for enc in encounters:
                            print(f"  - {enc}")
                    else:
                        print("No encounters found for patient.")
                else:
                    print("No patient ID available to fetch encounters.")
            except DatabaseError as e:
                print(f"Database error: {e}")

            # Example: Update an encounter
            try:
                if encounter_id:
                    updated = update_encounter(conn, encounter_id, notes="Patient feeling better")
                    if updated:
                        print(f"Encounter {encounter_id} updated successfully.")
                    else:
                        print(f"Encounter {encounter_id} not found or no updates applied.")
                else:
                    print("No encounter ID available to update.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except EncounterNotFoundError as e:
                print(f"Encounter not found error: {e}")

            # Example: Delete an encounter
            try:
                if encounter_id:
                    deleted = delete_encounter(conn, encounter_id)
                    if deleted:
                        print(f"Encounter {encounter_id} deleted successfully.")
                    else:
                        print(f"Encounter {encounter_id} not found for deletion.")
                else:
                    print("No encounter ID available to delete.")
            except DatabaseError as e:
                print(f"Database error: {e}")
            except EncounterNotFoundError as e:
                print(f"Encounter not found error: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            put_db_connection(conn)  # Return the connection to the pool
        close_db_pool()