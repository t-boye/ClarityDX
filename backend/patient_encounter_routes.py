from flask import Blueprint, request, jsonify
from datetime import date, time, datetime
import logging
import random  # <--- ADDED THIS LINE
from utils.db_utils import (
    get_db_connection,
    put_db_connection,
    close_db_pool,
    create_patient,
    fetch_patient_by_id,
    fetch_all_patients,
    update_patient,
    delete_patient,
    create_encounter,
    fetch_encounters_by_patient,
    update_encounter,
    delete_encounter,
    fetch_encounter_by_id,
    DatabaseError,
    PatientNotFoundError,
    EncounterNotFoundError,
    create_record,
    fetch_records_by_encounter,
    fetch_record_by_id,
    update_record,
    delete_record,
    RecordNotFoundError,
)
from pydantic import BaseModel, Field, ValidationError  # Import ValidationError
from typing import Any, Dict, List, Optional
import psycopg2.extensions

patient_encounter_bp = Blueprint('patient_encounter', __name__)


class PatientCreateData(BaseModel):
    name: str = Field(..., min_length=1)  # Name is required, min length 1
    age: Optional[int] = Field(default=None, ge=0)  # Age is optional, must be >= 0
    gender: Optional[str] = Field(default=None, max_length=50)  # Gender is optional, max length 50
    contact_info: Optional[str] = None


class EncounterCreateData(BaseModel):
    patient_id: int = Field(..., gt=0, description="The ID of the patient")
    encounter_date: Optional[date] = Field(default=None, description="Date of encounter")
    encounter_time: Optional[time] = Field(default=None, description="Time of encounter")
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[int] = None


class RecordCreateData(BaseModel):
    encounter_id: int = Field(..., gt=0, description="The ID of the encounter")
    record_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    details: str = Field(..., min_length=1, description="Details of the record")


@patient_encounter_bp.route('/api/patients/<int:patient_id>/encounters', methods=['POST'])
def create_new_encounter(patient_id: int):
    """
    Creates a new encounter record for a specific patient.
    Automatically sets the encounter date and time using the system's current datetime.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        data: Dict[str, Any] = request.get_json()
        logging.info(f"Received data for creating encounter: {data}")

        # Inject current system date and time
        now = datetime.now()
        data["encounter_date"] = now.date().isoformat()  # 'YYYY-MM-DD'
        data["encounter_time"] = now.time().strftime("%H:%M:%S")  # 'HH:MM:SS'

        try:
            validated_data = EncounterCreateData.model_validate(
                {**data, "patient_id": patient_id}
            )
        except ValidationError as e:
            return jsonify({"error": f"Invalid input data: {e.errors()}"}), 400

        encounter_id = create_encounter(
            conn=conn,
            patient_id=validated_data.patient_id,
            encounter_date=validated_data.encounter_date,
            encounter_time=validated_data.encounter_time,
            chief_complaint=validated_data.chief_complaint,
            notes=validated_data.notes,
            user_id=validated_data.user_id,
        )

        if encounter_id:
            new_encounter = fetch_encounter_by_id(conn=conn, encounter_id=encounter_id)
            if new_encounter:
                # 🔥 Fix: Serialize any non-JSON-safe values
                if isinstance(new_encounter.get("encounter_date"), datetime):
                    new_encounter["encounter_date"] = new_encounter["encounter_date"].date().isoformat()
                elif hasattr(new_encounter.get("encounter_date"), "isoformat"):
                    new_encounter["encounter_date"] = new_encounter["encounter_date"].isoformat()

                if hasattr(new_encounter.get("encounter_time"), "strftime"):
                    new_encounter["encounter_time"] = new_encounter["encounter_time"].strftime("%H:%M:%S")

                return jsonify({"message": "Encounter created successfully", "encounter": new_encounter}), 201
            else:
                return jsonify({"message": "Encounter created successfully", "encounter_id": encounter_id}), 201
        else:
            return jsonify({"error": "Failed to create encounter"}), 500

    except DatabaseError as e:
        if conn:
            conn.rollback()
        logging.error(f"Database error creating encounter: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Unexpected error creating encounter: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)


@patient_encounter_bp.route('/api/patients', methods=['GET'])
def get_all_patients():
    """Retrieves a list of all patient records."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        patients = fetch_all_patients(conn)
        return jsonify(patients), 200
    except DatabaseError as e:
        logging.error(f"Database error fetching patients: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error fetching patients: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if conn:
            put_db_connection(conn)


@patient_encounter_bp.route('/api/patients', methods=['POST'])
def create_new_patient():
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        data: Dict[str, Any] = request.get_json()
        logging.info(f"Received data for creating patient: {data}")

        try:
            validated_data = PatientCreateData.model_validate(data)
        except ValidationError as e:
            return jsonify({"error": f"Invalid input data: {e.errors()}"}), 400

        # Generate unique patient code: e.g., TSys-2345
        unique_code = f"TSys-{random.randint(1000, 9999)}" # 'random' is now defined!

        patient_id = create_patient(
            conn=conn,
            name=validated_data.name,
            age=validated_data.age,
            gender=validated_data.gender,
            contact_info=validated_data.contact_info,
            unique_patient_code=unique_code  # Make sure the DB supports this field
        )
        if patient_id:
            new_patient = fetch_patient_by_id(conn=conn, patient_id=patient_id)
            if new_patient:
                return jsonify({
                    "message": "Patient created successfully",
                    "patient": new_patient
                }), 201
            else:
                return jsonify({"error": "Failed to retrieve created patient"}), 500
        else:
            return jsonify({"error": "Failed to create patient"}), 500

    except DatabaseError as e:
        logging.error(f"Database error creating patient: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Unexpected error creating patient: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if conn:
            put_db_connection(conn)



@patient_encounter_bp.route('/api/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id: int):
    """Retrieves a single patient's details by ID."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        logging.info(f"Fetching patient with ID: {patient_id}")
        patient = fetch_patient_by_id(conn=conn, patient_id=patient_id)

        if patient:
            return jsonify(patient), 200
        else:
            return jsonify({"error": "Patient not found"}), 404

    except DatabaseError as e:
        logging.error(f"Database error fetching patient: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except PatientNotFoundError:
        return jsonify({"error": "Patient not found"}), 404
    except Exception as e:
        logging.error(f"Unexpected error fetching patient: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)


@patient_encounter_bp.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_existing_patient(patient_id: int):
    """Updates an existing patient's details."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        data: Dict[str, Any] = request.get_json()
        logging.info(f"Received data for updating patient {patient_id}: {data}")

        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        updated_rows = update_patient(conn=conn, patient_id=patient_id, update_data=data)

        if updated_rows > 0:
            # Fetch the updated patient details
            updated_patient = fetch_patient_by_id(conn=conn, patient_id=patient_id)
            if updated_patient:
                return jsonify({"message": "Patient updated successfully", "patient": updated_patient}), 200
            else:
                return jsonify({"error": "Failed to retrieve updated patient details"}), 500
        else:
            return jsonify({"error": "Patient not found or no updates applied"}), 404

    except DatabaseError as e:
        logging.error(f"Database error updating patient: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except PatientNotFoundError:
        return jsonify({"error": "Patient not found"}), 404
    except Exception as e:
        conn.rollback()
        logging.error(f"Unexpected error updating patient: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)


@patient_encounter_bp.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_existing_patient(patient_id: int):
    """Deletes an existing patient record."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        deleted_rows = delete_patient(conn=conn, patient_id=patient_id)

        if deleted_rows > 0:
            return jsonify({"message": "Patient deleted successfully"}), 200
        else:
            return jsonify({"error": "Patient not found"}), 404

    except DatabaseError as e:
        logging.error(f"Database error deleting patient: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except PatientNotFoundError:
        return jsonify({"error": "Patient not found"}), 404
    except Exception as e:
        conn.rollback()
        logging.error(f"Unexpected error deleting patient: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)


@patient_encounter_bp.route('/api/patients/<int:patient_id>/encounters', methods=['GET'])
def get_patient_encounters(patient_id: int):
    """
    Retrieves all encounter records for a given patient.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        logging.info(f"Fetching encounters for patient ID: {patient_id}")
        encounters = fetch_encounters_by_patient(conn=conn, patient_id=patient_id)

        # Convert time objects to strings
        for encounter in encounters:
            if isinstance(encounter['encounter_time'], time):
                encounter['encounter_time'] = encounter['encounter_time'].strftime("%H:%M")  # Format as needed

        if encounters:
            return jsonify(encounters), 200
        else:
            return jsonify({"error": "No encounters found for patient"}), 404

    except DatabaseError as e:
        logging.error(f"Database error fetching encounters: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error fetching encounters: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)


@patient_encounter_bp.route('/api/encounters/<int:encounter_id>', methods=['GET'])
def get_encounter(encounter_id: int):
    """Retrieves a single encounter's details by ID."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        logging.info(f"Fetching encounter with ID: {encounter_id}")
        encounter = fetch_encounter_by_id(conn=conn, encounter_id=encounter_id)

        if encounter:
            # Convert datetime.time object to string if it exists
            if 'encounter_time' in encounter and isinstance(encounter['encounter_time'], time):
                encounter['encounter_time'] = encounter['encounter_time'].isoformat()
            return jsonify(encounter), 200
        else:
            return jsonify({"error": "Encounter not found"}), 404

    except DatabaseError as e:
        logging.error(f"Database error fetching encounter: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error fetching encounter: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)




@patient_encounter_bp.route('/api/encounters/<int:encounter_id>', methods=['PUT'])
def update_existing_encounter(encounter_id: int):
    """Updates an existing encounter record."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        data: Dict[str, Any] = request.get_json()
        logging.info(f"Received data for updating encounter {encounter_id}: {data}")

        if not data:
            return jsonify({"error": "No data provided for update"}), 400

        updated_rows = update_encounter(conn=conn, encounter_id=encounter_id, update_data=data)

        if updated_rows > 0:
            # Fetch the updated encounter details
            updated_encounter = fetch_encounter_by_id(conn=conn, encounter_id=encounter_id)
            if updated_encounter:
                return jsonify({"message": "Encounter updated successfully", "encounter": updated_encounter}), 200
            else:
                return jsonify({"error": "Failed to retrieve updated encounter details"}), 500
        else:
            return jsonify({"error": "Encounter not found or no updates applied"}), 404

    except DatabaseError as e:
        logging.error(f"Database error updating encounter: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except EncounterNotFoundError:
        return jsonify({"error": "Encounter not found"}), 404
    except Exception as e:
        conn.rollback()
        logging.error(f"Unexpected error updating encounter: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)


@patient_encounter_bp.route('/api/encounters/<int:encounter_id>', methods=['DELETE'])
def delete_existing_encounter(encounter_id: int):
    """Deletes an existing encounter record."""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        deleted_rows = delete_encounter(conn=conn, encounter_id=encounter_id)

        if deleted_rows > 0:
            return jsonify({"message": "Encounter deleted successfully"}), 200
        else:
            return jsonify({"error": "Encounter not found"}), 404

    except DatabaseError as e:
        logging.error(f"Database error deleting encounter: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    except EncounterNotFoundError:
        return jsonify({"error": "Encounter not found"}), 404
    except Exception as e:
        conn.rollback()
        logging.error(f"Unexpected error deleting encounter: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if conn:
            put_db_connection(conn)


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
        cur.execute("SELECT encounter_id, patient_id, encounter_date, encounter_time, chief_complaint, notes, user_id FROM encounters WHERE encounter_id = %s", (encounter_id,))
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