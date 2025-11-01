"""
Netlify Serverless Function: Patient Management
Endpoint: /.netlify/functions/patients
Methods: GET, POST, PUT, DELETE
"""

import json
import logging
import sys
import os
import re

# Add shared modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))

from db_utils import (
    get_db_connection,
    put_db_connection,
    create_patient,
    fetch_patient_by_id,
    fetch_all_patients,
    update_patient,
    delete_patient,
    DatabaseError,
    PatientNotFoundError
)
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatientCreateData(BaseModel):
    """Pydantic model for patient creation"""
    name: str = Field(..., min_length=1)
    age: Optional[int] = Field(default=None, ge=0)
    gender: Optional[str] = Field(default=None, max_length=50)
    contact_info: Optional[str] = None


def handler(event, context):
    """
    Netlify serverless function handler for patient management.

    Supports:
    - GET /api/patients - List all patients
    - POST /api/patients - Create a patient
    - GET /api/patients/{id} - Get patient by ID
    - PUT /api/patients/{id} - Update patient
    - DELETE /api/patients/{id} - Delete patient
    """
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
        # Get database connection
        conn = get_db_connection()
        if not conn:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Database connection failed'})
            }

        method = event.get('httpMethod')
        path = event.get('path', '')

        # Extract patient_id from path if present
        # Path might be like: /.netlify/functions/patients/123
        path_match = re.search(r'/patients/(\d+)', path)
        patient_id = int(path_match.group(1)) if path_match else None

        # Route based on method and path
        if method == 'GET':
            if patient_id:
                # GET single patient
                return get_patient(conn, patient_id, headers)
            else:
                # GET all patients
                return get_all_patients(conn, headers)

        elif method == 'POST':
            # CREATE patient
            return create_new_patient(conn, event, headers)

        elif method == 'PUT' and patient_id:
            # UPDATE patient
            return update_existing_patient(conn, patient_id, event, headers)

        elif method == 'DELETE' and patient_id:
            # DELETE patient
            return delete_existing_patient(conn, patient_id, headers)

        else:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid request'})
            }

    except Exception as e:
        logger.exception(f"Unhandled error in patient management: {e}")
        if conn:
            conn.rollback()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }
    finally:
        if conn:
            put_db_connection(conn)


def get_all_patients(conn, headers):
    """Retrieve all patients"""
    try:
        patients = fetch_all_patients(conn)
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(patients)
        }
    except DatabaseError as e:
        logger.error(f"Database error fetching patients: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }


def get_patient(conn, patient_id, headers):
    """Retrieve a single patient by ID"""
    try:
        patient = fetch_patient_by_id(conn=conn, patient_id=patient_id)
        if patient:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(patient)
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Patient not found'})
            }
    except PatientNotFoundError:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Patient not found'})
        }
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }


def create_new_patient(conn, event, headers):
    """Create a new patient"""
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        logger.info(f"Creating patient with data: {body}")

        # Validate input
        try:
            validated_data = PatientCreateData(**body)
        except ValidationError as e:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': f'Invalid input data: {e.errors()}'})
            }

        # Generate unique patient code
        unique_code = f"TSys-{random.randint(1000, 9999)}"

        # Create patient
        patient_id = create_patient(
            conn=conn,
            name=validated_data.name,
            age=validated_data.age,
            gender=validated_data.gender,
            contact_info=validated_data.contact_info,
            unique_patient_code=unique_code
        )

        if patient_id:
            new_patient = fetch_patient_by_id(conn=conn, patient_id=patient_id)
            if new_patient:
                return {
                    'statusCode': 201,
                    'headers': headers,
                    'body': json.dumps({
                        'message': 'Patient created successfully',
                        'patient': new_patient
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'error': 'Failed to retrieve created patient'})
                }
        else:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Failed to create patient'})
            }

    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }


def update_existing_patient(conn, patient_id, event, headers):
    """Update an existing patient"""
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        logger.info(f"Updating patient {patient_id} with data: {body}")

        if not body:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'No data provided for update'})
            }

        # Update patient
        updated_rows = update_patient(
            conn=conn,
            patient_id=patient_id,
            name=body.get('name'),
            age=body.get('age'),
            gender=body.get('gender'),
            contact_info=body.get('contact_info')
        )

        if updated_rows > 0:
            updated_patient = fetch_patient_by_id(conn=conn, patient_id=patient_id)
            if updated_patient:
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'message': 'Patient updated successfully',
                        'patient': updated_patient
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'error': 'Failed to retrieve updated patient'})
                }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Patient not found or no updates applied'})
            }

    except PatientNotFoundError:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Patient not found'})
        }
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }


def delete_existing_patient(conn, patient_id, headers):
    """Delete a patient"""
    try:
        deleted_rows = delete_patient(conn=conn, patient_id=patient_id)

        if deleted_rows > 0:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'Patient deleted successfully'})
            }
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Patient not found'})
            }

    except PatientNotFoundError:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Patient not found'})
        }
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
