import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional

# Assuming you have these functions in a database_utils.py file
from backend.utils.db_utils import (
    get_db_connection,
    create_patient,
    fetch_patient_by_id,
    update_patient,
    delete_patient,
    fetch_encounters_by_patient  # If you want to include encounters in patient details
)

patient_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@patient_bp.route('', methods=['POST'])
def create_new_patient():
    """
    Creates a new patient record.
    """
    conn = get_db_connection()  # Get a database connection
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data: Dict[str, Any] = request.get_json()
        logging.info(f"Received data for creating patient: {data}")

        # Basic input validation (consider Pydantic for more robust validation)
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is a required field'}), 400

        patient_id = create_patient(
            conn=conn,  # Pass the connection to create_patient
            name=data['name'],
            age=data.get('age'),
            gender=data.get('gender'),
            contact_info=data.get('contact_info')
        )

        if patient_id:
            return jsonify({'message': 'Patient created successfully', 'patient_id': patient_id}), 201
        else:
            return jsonify({'error': 'Failed to create patient'}), 500

    except Exception as e:
        conn.rollback()  # Rollback in case of database errors
        logging.error(f"Error creating patient: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        conn.close()  # Close the connection in the 'finally' block


@patient_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id: int):
    """
    Retrieves a single patient's details by ID.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        logging.info(f"Fetching patient with ID: {patient_id}")
        patient = fetch_patient_by_id(conn=conn, patient_id=patient_id)  # Pass the connection

        if patient:
            return jsonify(patient), 200
        else:
            return jsonify({'error': 'Patient not found'}), 404

    except Exception as e:
        logging.error(f"Error fetching patient: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        conn.close()  # Close the connection


@patient_bp.route('/<int:patient_id>', methods=['PUT'])
def update_existing_patient(patient_id: int):
    """
    Updates an existing patient's details.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data: Dict[str, Any] = request.get_json()
        logging.info(f"Received data for updating patient {patient_id}: {data}")

        updated = update_patient(
            conn=conn,
            patient_id=patient_id,
            name=data.get('name'),
            age=data.get('age'),
            gender=data.get('gender'),
            contact_info=data.get('contact_info')
        )

        if updated:
            return jsonify({'message': 'Patient updated successfully'}), 200
        else:
            return jsonify({'error': 'Patient not found or no updates provided'}), 404

    except Exception as e:
        conn.rollback()  # Rollback in case of database errors
        logging.error(f"Error updating patient {patient_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        conn.close()  # Close the connection


@patient_bp.route('/<int:patient_id>', methods=['DELETE'])
def delete_existing_patient(patient_id: int):
    """
    Deletes an existing patient record.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        logging.info(f"Deleting patient with ID: {patient_id}")
        deleted = delete_patient(conn=conn, patient_id=patient_id)

        if deleted:
            return jsonify({'message': 'Patient deleted successfully'}), 200
        else:
            return jsonify({'error': 'Patient not found'}), 404

    except Exception as e:
        conn.rollback()  # Rollback in case of database errors
        logging.error(f"Error deleting patient {patient_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        conn.close()  # Close the connection


@patient_bp.route('/<int:patient_id>/encounters', methods=['GET'])
def get_patient_encounters(patient_id: int):
    """
    Retrieves all encounter records for a given patient.
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        logging.info(f"Fetching encounters for patient ID: {patient_id}")
        encounters = fetch_encounters_by_patient(conn=conn, patient_id=patient_id)

        if encounters:
            return jsonify(encounters), 200
        else:
            return jsonify({'error': 'No encounters found for patient'}), 404

    except Exception as e:
        logging.error(f"Error fetching encounters: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        conn.close()