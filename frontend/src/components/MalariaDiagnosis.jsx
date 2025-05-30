import React, { useState } from "react";
import { Dialog, DialogPanel } from "@headlessui/react";

const MalariaDiagnosis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [probability, setProbability] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isNonSmear, setIsNonSmear] = useState(false); // New state for non-smear detection

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      alert("Please select an image first.");
      return;
    }

    setLoading(true);
    setResult(null);
    setProbability(null);
    setIsNonSmear(false); // Reset non-smear state

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/image-processing/process-image",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      console.log("API Response:", data);

      if (data && data.diagnosis) {
        setResult(data.diagnosis);
        setProbability(data.probability); // Use the direct probability from the backend
        setIsNonSmear(data.isNonSmear); // Set non-smear flag based on backend response
      } else {
        setResult("No diagnosis result found.");
      }
    } catch (error) {
      console.error("Error uploading image:", error);
      setResult("Error processing image. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 flex flex-col items-center">
      <h2 className="text-2xl font-semibold mb-4">Malaria Diagnosis</h2>
      <p>Upload your blood smear image to check for Malaria.</p>

      <input
        type="file"
        className="border p-2 rounded w-full mt-2"
        onChange={handleFileChange}
      />

      <button
        onClick={handleSubmit}
        className="bg-green-500 text-white p-2 rounded mt-2"
        disabled={loading}
      >
        {loading ? "Processing..." : "Submit"}
      </button>

      {loading && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <p className="text-gray-700">Processing Diagnosis...</p>
          </div>
        </div>
      )}

      <Dialog
        open={!!result}
        onClose={() => {
          setResult(null);
          setProbability(null);
          setIsNonSmear(false);
        }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      >
        <DialogPanel className="w-96 bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-lg font-semibold">Diagnosis Result</h2>
          {probability !== null && (
            <p className="mt-2 text-gray-700">
              Probability: {probability.toFixed(2)}
            </p>
          )}
          {isNonSmear && (
            <p className="mt-2 text-red-600">
              This image is not a blood smear. Please upload a blood smear
              image.
            </p>
          )}
          <p className="mt-4 text-gray-700">{result}</p>

          <div className="mt-4 text-sm text-gray-500">
            <p>
              <strong>Disclaimer:</strong> The information provided here is for
              educational purposes only and should not be considered a
              substitute for professional medical advice. Always consult with a
              qualified healthcare provider for diagnosis and treatment.
            </p>
          </div>
          <div className="mt-6 flex justify-end space-x-4">
            <button
              onClick={() => {
                setResult(null);
                setProbability(null);
                setIsNonSmear(false);
              }}
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

export default MalariaDiagnosis;
