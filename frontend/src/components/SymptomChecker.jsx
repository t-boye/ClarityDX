import React, { useState } from "react";

const SymptomChecker = () => {
  const [symptoms, setSymptoms] = useState("");
  const [result, setResult] = useState(null);

  const checkSymptoms = () => {
    if (symptoms.includes("fever") && symptoms.includes("chills")) {
      setResult("Possible Malaria. Please visit a doctor.");
    } else {
      setResult("No strong match found. Consider consulting a specialist.");
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Symptom Checker</h2>
      <textarea
        value={symptoms}
        onChange={(e) => setSymptoms(e.target.value)}
        placeholder="Enter your symptoms (e.g., fever, chills, headache)..."
        className="w-full p-2 border rounded"
      />
      <button
        onClick={checkSymptoms}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Check Symptoms
      </button>
      {result && <p className="mt-4 text-red-500">{result}</p>}
    </div>
  );
};

export default SymptomChecker;
