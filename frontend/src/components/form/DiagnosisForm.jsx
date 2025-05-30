import React, { useState } from "react";
import { Dialog, DialogPanel } from "@headlessui/react";

const DiagnosisForm = () => {
  const [input, setInput] = useState({
    age: "",
    gender: "",
    travelHistory: "",
    mosquitoExposure: "",
    symptoms: [],
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (type === "checkbox") {
      setInput((prevInput) => ({
        ...prevInput,
        symptoms: checked
          ? [...prevInput.symptoms, value]
          : prevInput.symptoms.filter((symptom) => symptom !== value),
      }));
    } else {
      setInput({ ...input, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      // Validate input data on the frontend (basic)
      if (!input.age || isNaN(Number(input.age)) || Number(input.age) < 0) {
        throw new Error("Invalid age. Age must be a non-negative number.");
      }
      if (
        !input.gender ||
        !["male", "female"].includes(input.gender.toLowerCase())
      ) {
        throw new Error("Invalid gender. Please select male or female.");
      }
      if (
        !input.travelHistory ||
        !["yes", "no"].includes(input.travelHistory.toLowerCase())
      ) {
        throw new Error("Invalid travel history. Please select yes or no.");
      }
      if (
        !input.mosquitoExposure ||
        !["yes", "no", "maybe"].includes(input.mosquitoExposure.toLowerCase())
      ) {
        throw new Error(
          "Invalid mosquito exposure. Please select yes, no, or maybe."
        );
      }

      const response = await fetch(
        "http://127.0.0.1:5000/api/malaria-risk", // Updated API endpoint
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(input),
        }
      );

      if (!response.ok)
        throw new Error("Failed to diagnose based on symptoms.");

      const data = await response.json();
      setResult({ type: "Rule-Based", ...data }); // Set type to Rule-Based
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Expanded Symptom Options (for display)
  const symptomOptions = [
    { value: "fever", label: "Fever" },
    { value: "chills", label: "Chills" },
    { value: "headache", label: "Headache" },
    { value: "fatigue", label: "Fatigue" },
    { value: "nausea", label: "Nausea" },
    { value: "vomiting", label: "Vomiting" }, // Added
    { value: "muscle-pain", label: "Muscle Pain" }, // Added
    { value: "severe-anemia", label: "Severe Anemia" },
    { value: "seizures", label: "Seizures" },
    { value: "confusion", label: "Confusion" },
    { value: "abdominal-pain", label: "Abdominal Pain" }, // Added
    { value: "cough", label: "Cough" }, // Added
  ];

  return (
    <div className="container mx-auto p-6 bg-white shadow-lg rounded-md">
      <h2 className="text-2xl text-center font-bold mb-4">
        Malaria Risk Assessment
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-gray-700 font-bold" htmlFor="age">
            Age:
          </label>
          <input
            type="number"
            id="age"
            name="age"
            value={input.age}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
            required
          />
        </div>

        <div>
          <label className="block text-gray-700 font-bold" htmlFor="gender">
            Gender:
          </label>
          <select
            id="gender"
            name="gender"
            value={input.gender}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
            required
          >
            <option value="">Select Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>

        <div>
          <label
            className="block text-gray-700 font-bold"
            htmlFor="travelHistory"
          >
            Recent Travel to Malaria-Prone Areas:
          </label>
          <select
            id="travelHistory"
            name="travelHistory"
            value={input.travelHistory}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Select</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
          </select>
        </div>

        <div>
          <label
            className="block text-gray-700 font-bold"
            htmlFor="mosquitoExposure"
          >
            Frequent Mosquito Bites:
          </label>
          <select
            id="mosquitoExposure"
            name="mosquitoExposure"
            value={input.mosquitoExposure}
            onChange={handleChange}
            className="w-full border rounded px-3 py-2"
          >
            <option value="">Select</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
            <option value="maybe">Maybe</option>
          </select>
        </div>

        <div>
          <label className="block text-gray-700 font-bold">
            Select Symptoms:
          </label>
          <div className="grid grid-cols-2 gap-2">
            {symptomOptions.map((symptom) => (
              <label key={symptom.value} className="flex items-center">
                <input
                  type="checkbox"
                  value={symptom.value}
                  onChange={handleChange}
                  className="mr-2"
                />
                {symptom.label}
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded ${
            loading ? "opacity-50 cursor-not-allowed" : ""
          }`}
        >
          {loading ? "Assessing Risk..." : "Assess Risk"}
        </button>

        {error && <p className="text-red-500">{error}</p>}
      </form>

      {/* Loading Indicator */}
      {loading && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <p className="text-gray-700">Processing Assessment...</p>
          </div>
        </div>
      )}

      {/* Diagnosis Result Popup */}
      <Dialog
        open={!!result}
        onClose={() => setResult(null)}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      >
        <DialogPanel className="w-96 bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-lg font-semibold">Risk Assessment</h2>
          {result && (
            <>
              <p className="mt-4 text-gray-700">
                Risk Level: {result.risk_level}
              </p>
              <p className="mt-2 text-gray-700">
                Recommendation: {result.recommendation}
              </p>
              {result.additional_info && result.additional_info.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-md font-semibold">
                    Additional Information:
                  </h3>
                  <ul>
                    {result.additional_info.map((info, index) => (
                      <li key={index} className="list-disc ml-5">
                        {info}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
          <div className="mt-6 flex justify-end space-x-4">
            <button
              onClick={() => setResult(null)}
              className="px-4 py-2 bg-gray-300 rounded-md"
            >
              Close
            </button>
            <a
              href="/info"
              className="px-4 py-2 bg-blue-600 text-white rounded-md"
            >
              Learn More
            </a>
          </div>
        </DialogPanel>
      </Dialog>
    </div>
  );
};

export default DiagnosisForm;
