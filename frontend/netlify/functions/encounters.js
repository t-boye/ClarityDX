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

  const encounterMatch = event.path.match(/\/encounters\/(\d+)/);
  const patientMatch = event.path.match(/\/patients\/(\d+)\/encounters/);

  const encounterId = encounterMatch ? parseInt(encounterMatch[1]) : null;
  const patientId = patientMatch ? parseInt(patientMatch[1]) : null;

  try {
    switch (event.httpMethod) {
      case 'GET':
        if (encounterId) return await getEncounter(encounterId);
        if (patientId) return await getPatientEncounters(patientId);
        return { statusCode: 400, headers, body: JSON.stringify({ error: 'Patient ID or Encounter ID required' }) };
      case 'POST':
        if (!patientId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Patient ID required' }) };
        return await createEncounter(patientId, JSON.parse(event.body || '{}'));
      case 'PUT':
        if (!encounterId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Encounter ID required' }) };
        return await updateEncounter(encounterId, JSON.parse(event.body || '{}'));
      case 'DELETE':
        if (!encounterId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Encounter ID required' }) };
        return await deleteEncounter(encounterId);
      default:
        return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
    }
  } catch (error) {
    console.error('Encounter operation error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Internal server error', details: error.message })
    };
  }
};

async function getPatientEncounters(patientId) {
  const result = await pool.query(
    'SELECT * FROM encounters WHERE patient_id = $1 ORDER BY encounter_date DESC',
    [patientId]
  );
  return { statusCode: 200, headers, body: JSON.stringify(result.rows) };
}

async function getEncounter(id) {
  const result = await pool.query('SELECT * FROM encounters WHERE encounter_id = $1', [id]);
  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Encounter not found' }) };
  }
  return { statusCode: 200, headers, body: JSON.stringify(result.rows[0]) };
}

async function createEncounter(patientId, data) {
  const result = await pool.query(
    `INSERT INTO encounters (patient_id, encounter_date, encounter_time, chief_complaint, notes, user_id)
     VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
    [patientId, data.encounter_date, data.encounter_time, data.chief_complaint, data.notes, data.user_id]
  );
  return {
    statusCode: 201,
    headers,
    body: JSON.stringify({ message: 'Encounter created successfully', encounter: result.rows[0] })
  };
}

async function updateEncounter(id, data) {
  const fields = [];
  const values = [];
  let idx = 1;

  if (data.encounter_date) { fields.push(`encounter_date = $${idx++}`); values.push(data.encounter_date); }
  if (data.encounter_time) { fields.push(`encounter_time = $${idx++}`); values.push(data.encounter_time); }
  if (data.chief_complaint) { fields.push(`chief_complaint = $${idx++}`); values.push(data.chief_complaint); }
  if (data.notes !== undefined) { fields.push(`notes = $${idx++}`); values.push(data.notes); }

  if (fields.length === 0) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'No fields to update' }) };
  }

  fields.push(`updated_at = NOW()`);
  values.push(id);

  const result = await pool.query(
    `UPDATE encounters SET ${fields.join(', ')} WHERE encounter_id = $${idx} RETURNING *`,
    values
  );

  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Encounter not found' }) };
  }
  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({ message: 'Encounter updated successfully', encounter: result.rows[0] })
  };
}

async function deleteEncounter(id) {
  const result = await pool.query('DELETE FROM encounters WHERE encounter_id = $1 RETURNING *', [id]);
  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Encounter not found' }) };
  }
  return { statusCode: 200, headers, body: JSON.stringify({ message: 'Encounter deleted successfully' }) };
}
