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

  const pathMatch = event.path.match(/\/patients\/(\d+)/);
  const patientId = pathMatch ? parseInt(pathMatch[1]) : null;

  try {
    switch (event.httpMethod) {
      case 'GET':
        return patientId ? await getPatient(patientId) : await getAllPatients();
      case 'POST':
        return await createPatient(JSON.parse(event.body || '{}'));
      case 'PUT':
        if (!patientId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Patient ID required' }) };
        return await updatePatient(patientId, JSON.parse(event.body || '{}'));
      case 'DELETE':
        if (!patientId) return { statusCode: 400, headers, body: JSON.stringify({ error: 'Patient ID required' }) };
        return await deletePatient(patientId);
      default:
        return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
    }
  } catch (error) {
    console.error('Patient operation error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: 'Internal server error', details: error.message })
    };
  }
};

async function getAllPatients() {
  const result = await pool.query('SELECT * FROM patients ORDER BY created_at DESC');
  return { statusCode: 200, headers, body: JSON.stringify(result.rows) };
}

async function getPatient(id) {
  const result = await pool.query('SELECT * FROM patients WHERE patient_id = $1', [id]);
  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Patient not found' }) };
  }
  return { statusCode: 200, headers, body: JSON.stringify(result.rows[0]) };
}

async function createPatient(data) {
  const uniqueCode = `TSys-${Math.floor(100000 + Math.random() * 900000)}`;
  const result = await pool.query(
    `INSERT INTO patients (unique_patient_code, name, age, gender, contact_info)
     VALUES ($1, $2, $3, $4, $5) RETURNING *`,
    [uniqueCode, data.name, data.age, data.gender, data.contact_info]
  );
  return {
    statusCode: 201,
    headers,
    body: JSON.stringify({ message: 'Patient created successfully', patient: result.rows[0] })
  };
}

async function updatePatient(id, data) {
  const fields = [];
  const values = [];
  let idx = 1;

  if (data.name) { fields.push(`name = $${idx++}`); values.push(data.name); }
  if (data.age !== undefined) { fields.push(`age = $${idx++}`); values.push(data.age); }
  if (data.gender) { fields.push(`gender = $${idx++}`); values.push(data.gender); }
  if (data.contact_info) { fields.push(`contact_info = $${idx++}`); values.push(data.contact_info); }

  if (fields.length === 0) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'No fields to update' }) };
  }

  fields.push(`updated_at = NOW()`);
  values.push(id);

  const result = await pool.query(
    `UPDATE patients SET ${fields.join(', ')} WHERE patient_id = $${idx} RETURNING *`,
    values
  );

  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Patient not found' }) };
  }
  return {
    statusCode: 200,
    headers,
    body: JSON.stringify({ message: 'Patient updated successfully', patient: result.rows[0] })
  };
}

async function deletePatient(id) {
  const result = await pool.query('DELETE FROM patients WHERE patient_id = $1 RETURNING *', [id]);
  if (result.rows.length === 0) {
    return { statusCode: 404, headers, body: JSON.stringify({ error: 'Patient not found' }) };
  }
  return { statusCode: 200, headers, body: JSON.stringify({ message: 'Patient deleted successfully' }) };
}
