"""
Netlify Serverless Function: Encounter Management
Endpoint: /.netlify/functions/encounters
Methods: GET, POST, PUT, DELETE
"""

import json
import logging
import sys
import os
import re
from datetime import datetime

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from db_utils import (
    get_db_connection,
    put_db_connection,
    create_encounter,
    fetch_encounters_by_patient,
    fetch_encounter_by_id,
    update_encounter,
    delete_encounter,
    DatabaseError,
    EncounterNotFoundError
)
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
from datetime import date, time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EncounterCreateData(BaseModel):
    """Pydantic model for encounter creation"""
    patient_id: int = Field(..., gt=0)
    encounter_date: Optional[date] = None
    encounter_time: Optional[time] = None
    chief_complaint: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[int] = None


def handler(event, context):
    """Netlify serverless function handler for encounter management."""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Database connection failed'})
            }

        method = event.get('httpMethod')
        path = event.get('path', '')

        # Extract IDs from path
        encounter_match = re.search(r'/encounters/(\d+)', path)
        patient_match = re.search(r'/patients/(\d+)/encounters', path)

        encounter_id = int(encounter_match.group(1)) if encounter_match else None
        patient_id = int(patient_match.group(1)) if patient_match else None

        if method == 'GET':
            if encounter_id:
                return get_encounter(conn, encounter_id, headers)
            elif patient_id:
                return get_patient_encounters(conn, patient_id, headers)
            else:
                return {'statusCode': 400, 'headers': headers,
                        'body': json.dumps({'error': 'Missing patient_id or encounter_id'})}

        elif method == 'POST' and patient_id:
            return create_new_encounter(conn, patient_id, event, headers)

        elif method == 'PUT' and encounter_id:
            return update_existing_encounter(conn, encounter_id, event, headers)

        elif method == 'DELETE' and encounter_id:
            return delete_existing_encounter(conn, encounter_id, headers)

        else:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Invalid request'})}

    except Exception as e:
        logger.exception(f"Error in encounter management: {e}")
        if conn:
            conn.rollback()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
    finally:
        if conn:
            put_db_connection(conn)


def get_patient_encounters(conn, patient_id, headers):
    """Get all encounters for a patient"""
    try:
        encounters = fetch_encounters_by_patient(conn=conn, patient_id=patient_id)

        # Serialize time objects
        for encounter in encounters:
            if isinstance(encounter.get('encounter_time'), time):
                encounter['encounter_time'] = encounter['encounter_time'].strftime("%H:%M")

        return {'statusCode': 200 if encounters else 404, 'headers': headers,
                'body': json.dumps(encounters if encounters else {'error': 'No encounters found'})}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def get_encounter(conn, encounter_id, headers):
    """Get a single encounter"""
    try:
        encounter = fetch_encounter_by_id(conn=conn, encounter_id=encounter_id)
        if encounter:
            if 'encounter_time' in encounter and isinstance(encounter['encounter_time'], time):
                encounter['encounter_time'] = encounter['encounter_time'].isoformat()
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps(encounter)}
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Encounter not found'})}
    except Exception as e:
        logger.error(f"Error: {e}")
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def create_new_encounter(conn, patient_id, event, headers):
    """Create a new encounter"""
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})

        # Auto-set date and time
        now = datetime.now()
        body["encounter_date"] = now.date().isoformat()
        body["encounter_time"] = now.time().strftime("%H:%M:%S")

        validated_data = EncounterCreateData.model_validate({**body, "patient_id": patient_id})

        encounter_id = create_encounter(
            conn=conn,
            patient_id=validated_data.patient_id,
            encounter_date=validated_data.encounter_date,
            encounter_time=validated_data.encounter_time,
            chief_complaint=validated_data.chief_complaint,
            notes=validated_data.notes,
            user_id=validated_data.user_id
        )

        if encounter_id:
            new_encounter = fetch_encounter_by_id(conn=conn, encounter_id=encounter_id)
            return {'statusCode': 201, 'headers': headers,
                    'body': json.dumps({'message': 'Encounter created', 'encounter': new_encounter})}
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': 'Failed to create'})}
    except ValidationError as e:
        return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': e.errors()})}
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def update_existing_encounter(conn, encounter_id, event, headers):
    """Update an encounter"""
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        updated_rows = update_encounter(
            conn=conn,
            encounter_id=encounter_id,
            encounter_date=body.get('encounter_date'),
            encounter_time=body.get('encounter_time'),
            chief_complaint=body.get('chief_complaint'),
            notes=body.get('notes'),
            user_id=body.get('user_id')
        )

        if updated_rows > 0:
            updated = fetch_encounter_by_id(conn=conn, encounter_id=encounter_id)
            return {'statusCode': 200, 'headers': headers,
                    'body': json.dumps({'message': 'Updated successfully', 'encounter': updated})}
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def delete_existing_encounter(conn, encounter_id, headers):
    """Delete an encounter"""
    try:
        deleted = delete_encounter(conn=conn, encounter_id=encounter_id)
        if deleted > 0:
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'Deleted successfully'})}
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}
