const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

const headers = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
};

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const recordMatch = event.path.match(/\/records\/(\d+)/);
  const encounterMatch = event.path.match(/\/encounters\/(\d+)\/records/);

  const recordId = recordMatch ? parseInt(recordMatch[1]) : null;
  const encounterId = encounterMatch ? parseInt(encounterMatch[1]) : null;

  try {
    switch (event.httpMethod) {
      case 'GET':
        if (recordId) return await getRecord(recordId);
        if (encounterId) return await getEncounterRecords(encounterId);
        return { statusCode: 400, headers, body: JSON.stringify({ error: 'Encounter ID or Record ID required' }) };
      case 'POST':
        if (!encounterId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Encounter ID required' }) };
        return await createRecord(encounterId, JSON.parse(event.body || '{}'));
      case 'PUT':
        if (!recordId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Record ID required' }) };
        return await updateRecord(recordId, JSON.parse(event.body || '{}'));
      case 'DELETE':
        if (!recordId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Record ID required' }) };
        return await deleteRecord(recordId);
      default:
        return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
    }
  } catch (error) {
    console.error('Record operation error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Internal server error', details: error.message })
    };
  }
};

async function getEncounterRecords(encounterId) {
  const result = await pool.query(
    'SELECT * FROM records WHERE encounter_id = $1 ORDER BY record_date DESC',
    [encounterId]
  );
  return { statusCode: 200, headers, body: JSON.stringify(result.rows) };
}

async function getRecord(id) {
  const result = await pool.query('SELECT * FROM records WHERE record_id = $1', [id]);
  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Record not found' }) };
  }
  return { statusCode: 200, headers, body: JSON.stringify(result.rows[0]) };
}

async function createRecord(encounterId, data) {
  const result = await pool.query(
    `INSERT INTO records (encounter_id, record_date, details, user_id)
     VALUES ($1, $2, $3, $4) RETURNING *`,
    [encounterId, data.record_date, data.details, data.user_id]
  );
  return {
    statusCode: 201,
    headers,
    body: JSON.stringify({ message: 'Record created successfully', record: result.rows[0] })
  };
}

async function updateRecord(id, data) {
  const fields = [];
  const values = [];
  let idx = 1;

  if (data.record_date) { fields.push(`record_date = $${idx++}`); values.push(data.record_date); }
  if (data.details) { fields.push(`details = $${idx++}`); values.push(data.details); }

  if (fields.length === 0) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'No fields to update' }) };
  }

  fields.push(`updated_at = NOW()`);
  values.push(id);

  const result = await pool.query(
    `UPDATE records SET ${fields.join(', ')} WHERE record_id = $${idx} RETURNING *`,
    values
  );

  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Record not found' }) };
  }
  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({ message: 'Record updated successfully', record: result.rows[0] })
  };
}

async function deleteRecord(id) {
  const result = await pool.query('DELETE FROM records WHERE record_id = $1 RETURNING *', [id]);
  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Record not found' }) };
  }
  return { statusCode: 200, headers, body: JSON.stringify({ message: 'Record deleted successfully' }) };
}
