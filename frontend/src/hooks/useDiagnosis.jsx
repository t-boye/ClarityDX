// hooks/useDiagnosis.js
import { useState } from 'react';
import { diagnoseMalaria } from '../services/diagnosis_service';

export const useDiagnosis = () => {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const diagnose = async (input) => {
    setLoading(true);
    try {
      const data = await diagnoseMalaria(input);
      setResult(data);
      setError(null);
    } catch (err) {
      setError(err.message); // Or err.response.data.message for more specific backend errors
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return { diagnose, result, error, loading };
};