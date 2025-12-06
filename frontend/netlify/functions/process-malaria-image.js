const fetch = require('node-fetch');

const BACKEND_URL = process.env.BACKEND_URL || 'https://claritydx-backend.onrender.com';

const headers = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type'
};

exports.handler = async (event) => {
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    const response = await fetch(`${BACKEND_URL}/api/image-processing/process-image`, {
      method: 'POST',
      headers: {
        'Content-Type': event.headers['content-type'] || 'application/json'
      },
      body: event.body
    });

    const data = await response.json();

    return {
      statusCode: response.status,
      headers,
      body: JSON.stringify(data)
    };
  } catch (error) {
    console.error('Malaria image processing error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        details: error.message,
        medical_disclaimer: 'This system is informational only and not a substitute for professional medical advice.'
      })
    };
  }
};
