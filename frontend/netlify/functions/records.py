"""
Netlify Serverless Function: Record Management
Endpoint: /.netlify/functions/records
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
    create_record,
    fetch_records_by_encounter,
    fetch_record_by_id,
    update_record,
    delete_record,
    DatabaseError,
    RecordNotFoundError
)
from pydantic import BaseModel, Field, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecordCreateData(BaseModel):
    """Pydantic model for record creation"""
    encounter_id: int = Field(..., gt=0)
    record_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    details: str = Field(..., min_length=1)


def handler(event, context):
    """Netlify serverless function handler for record management."""
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

        # Extract IDs
        record_match = re.search(r'/records/(\d+)', path)
        encounter_match = re.search(r'/encounters/(\d+)/records', path)

        record_id = int(record_match.group(1)) if record_match else None
        encounter_id = int(encounter_match.group(1)) if encounter_match else None

        if method == 'GET':
            if record_id:
                return get_record(conn, record_id, headers)
            elif encounter_id:
                return get_encounter_records(conn, encounter_id, headers)
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Missing ID'})}

        elif method == 'POST' and encounter_id:
            return create_new_record(conn, encounter_id, event, headers)

        elif method == 'PUT' and record_id:
            return update_existing_record(conn, record_id, event, headers)

        elif method == 'DELETE' and record_id:
            return delete_existing_record(conn, record_id, headers)

        return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'Invalid request'})}

    except Exception as e:
        logger.exception(f"Error: {e}")
        if conn:
            conn.rollback()
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}
    finally:
        if conn:
            put_db_connection(conn)


def get_encounter_records(conn, encounter_id, headers):
    """Get all records for an encounter"""
    try:
        records = fetch_records_by_encounter(conn=conn, encounter_id=encounter_id)
        return {'statusCode': 200 if records else 404, 'headers': headers,
                'body': json.dumps(records if records else {'error': 'No records found'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def get_record(conn, record_id, headers):
    """Get a single record"""
    try:
        record = fetch_record_by_id(conn=conn, record_id=record_id)
        if record:
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps(record)}
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def create_new_record(conn, encounter_id, event, headers):
    """Create a new record"""
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        validated_data = RecordCreateData.model_validate({**body, "encounter_id": encounter_id})

        record_id = create_record(
            conn=conn,
            encounter_id=validated_data.encounter_id,
            record_date=validated_data.record_date,
            details=validated_data.details
        )

        if record_id:
            new_record = fetch_record_by_id(conn=conn, record_id=record_id)
            return {'statusCode': 201, 'headers': headers,
                    'body': json.dumps({'message': 'Record created', 'record': new_record})}
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': 'Failed'})}
    except ValidationError as e:
        return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': e.errors()})}
    except Exception as e:
        conn.rollback()
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def update_existing_record(conn, record_id, event, headers):
    """Update a record"""
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        updated = update_record(
            conn=conn,
            record_id=record_id,
            record_date=body.get('record_date'),
            details=body.get('details'),
            user_id=body.get('user_id')
        )

        if updated > 0:
            record = fetch_record_by_id(conn=conn, record_id=record_id)
            return {'statusCode': 200, 'headers': headers,
                    'body': json.dumps({'message': 'Updated', 'record': record})}
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
    except Exception as e:
        conn.rollback()
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}


def delete_existing_record(conn, record_id, headers):
    """Delete a record"""
    try:
        deleted = delete_record(conn=conn, record_id=record_id)
        if deleted > 0:
            return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'Deleted'})}
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'Not found'})}
    except Exception as e:
        conn.rollback()
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}
