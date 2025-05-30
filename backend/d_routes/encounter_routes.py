import logging
from flask import Blueprint, request, jsonify
from typing import Optional, Dict, Any

# Assuming you have these functions in a database_utils.py file
from backend.d_utils.db_utils import (
    create_encounter,
    fetch_encounters_by_patient,
    update_encounter,
    delete_encounter,
)

encounter_bp = Blueprint('encounters', __name__, url_prefix='/api/encounters')  # Use a Blueprint

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@encounter_bp.route('', methods=['POST'])
def create_new_encounter():
    """
    Creates a new encounter record.
    """
    try:
        data: Dict[str, Any] = request.get_json()  # Explicitly type data
        logging.info(f"Received data for creating encounter: {data}")

        # Basic input validation (consider using Pydantic for more robust validation)
        if not all(key in data for key in ['patient_id', 'encounter_date']):
            return jsonify({'error': 'Missing required fields (patient_id, encounter_date)'}), 400

        encounter_id = create_encounter(
            patient_id=data['patient_id'],
            encounter_date=data['encounter_date'],
            encounter_time=data.get('encounter_time'),  # Use .get() for optional fields
            chief_complaint=data.get('chief_complaint'),
            notes=data.get('notes'),
            user_id=data.get('user_id')
        )

        if encounter_id:
            return jsonify({'message': 'Encounter created successfully', 'encounter_id': encounter_id}), 201
        else:
            return jsonify({'error': 'Failed to create encounter'}), 500

    except Exception as e:
        logging.error(f"Error creating encounter: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@encounter_bp.route('/<int:encounter_id>', methods=['GET'])
def get_encounter(encounter_id: int):
    """
    Fetches a single encounter by its ID (not implemented in database_utils yet).
    """
    logging.warning("get_encounter route not fully implemented")
    return jsonify({'error': 'Not implemented'}), 501


@encounter_bp.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient_encounters(patient_id: int):
    """
    Fetches all encounter records for a given patient.
    """
    try:
        logging.info(f"Fetching encounters for patient ID: {patient_id}")
        encounters = fetch_encounters_by_patient(patient_id)

        if encounters:
            return jsonify(encounters), 200
        else:
            return jsonify({'error': 'No encounters found for patient'}), 404

    except Exception as e:
        logging.error(f"Error fetching patient encounters: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@encounter_bp.route('/<int:encounter_id>', methods=['PUT'])
def update_existing_encounter(encounter_id: int):
    """
    Updates an existing encounter record.
    """
    try:
        data: Dict[str, Any] = request.get_json()
        logging.info(f"Received data for updating encounter {encounter_id}: {data}")

        updated = update_encounter(
            encounter_id=encounter_id,
            encounter_date=data.get('encounter_date'),
            encounter_time=data.get('encounter_time'),
            chief_complaint=data.get('chief_complaint'),
            notes=data.get('notes'),
            user_id=data.get('user_id')
        )

        if updated:
            return jsonify({'message': 'Encounter updated successfully'}), 200
        else:
            return jsonify({'error': 'Encounter not found or no updates provided'}), 404

    except Exception as e:
        logging.error(f"Error updating encounter {encounter_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@encounter_bp.route('/<int:encounter_id>', methods=['DELETE'])
def delete_existing_encounter(encounter_id: int):
    """
    Deletes an existing encounter record.
    """
    try:
        logging.info(f"Deleting encounter with ID: {encounter_id}")
        deleted = delete_encounter(encounter_id)

        if deleted:
            return jsonify({'message': 'Encounter deleted successfully'}), 200
        else:
            return jsonify({'error': 'Encounter not found'}), 404

    except Exception as e:
        logging.error(f"Error deleting encounter {encounter_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500