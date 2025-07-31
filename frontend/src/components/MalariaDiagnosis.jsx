import React, { useState } from "react";
import { BASE_API_URL } from "../utils/apiConfig";

const MalariaDiagnosis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [probability, setProbability] = useState(null);
  const [prescription, setPrescription] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isNonSmear, setIsNonSmear] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    // Reset previous results on new file select
    setResult(null);
    setProbability(null);
    setPrescription(null);
    setIsNonSmear(false);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      alert("Please select an image first.");
      return;
    }

    setLoading(true);
    setResult(null);
    setProbability(null);
    setPrescription(null);
    setIsNonSmear(false);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(
        `${BASE_API_URL}/image-processing/process-image`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      console.log("API Response:", data);

      if (response.ok && data && data.diagnosis_message) {
        setResult(data.diagnosis_message);
        setProbability(
          typeof data.probability === "number" ? data.probability : null
        );
        setPrescription(data.prescription || null);
        setIsNonSmear(data.isNonSmear === true);
      } else if (data && data.error) {
        setResult(data.error);
        setProbability(null);
        setPrescription(null);
        setIsNonSmear(false);
      } else {
        setResult("No diagnosis result found or unexpected response.");
        setProbability(null);
        setPrescription(null);
        setIsNonSmear(false);
      }
    } catch (error) {
      console.error("Error uploading image:", error);
      setResult("Error processing image. Please try again.");
      setProbability(null);
      setPrescription(null);
      setIsNonSmear(false);
    } finally {
      setLoading(false);
    }
  };

  // Helper to determine diagnosis status text and styles
  const getDiagnosisStatus = () => {
    if (isNonSmear) {
      return {
        text: "Non-Blood Smear Image Detected",
        bgColor: "bg-yellow-100",
        textColor: "text-yellow-900",
      };
    }
    if (result && result.toLowerCase().includes("parasitized")) {
      return {
        text: "Malaria Detected",
        bgColor: "bg-red-100",
        textColor: "text-red-800",
      };
    }
    if (result) {
      return {
        text: "No Malaria Detected",
        bgColor: "bg-green-100",
        textColor: "text-green-800",
      };
    }
    return { text: "", bgColor: "", textColor: "" };
  };

  const diagnosisStatus = getDiagnosisStatus();

  return (
    <div className="min-h-screen flex flex-col md:flex-row items-center justify-center p-4 md:p-8 bg-gradient-to-br from-blue-50 to-green-50 animate-gradient">
      {/* Input Section - Left Side */}
      <div className="bg-white rounded-3xl shadow-xl p-6 md:p-8 w-full md:w-1/2 max-w-sm md:max-w-md text-center space-y-4 md:mr-6 mb-6 md:mb-0">
        <h1 className="text-3xl font-extrabold text-gray-900" tabIndex={0}>
          Malaria Diagnosis
        </h1>
        <p className="text-sm md:text-base text-gray-600" tabIndex={0}>
          Upload a blood smear image to check for malaria.
        </p>

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="block w-full text-center py-2 md:py-3 border rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm md:text-base"
          disabled={loading}
          aria-label="Upload blood smear image"
        />

        <button
          onClick={handleSubmit}
          disabled={loading || !selectedFile}
          className={`w-full py-2 md:py-3 rounded-lg text-white font-semibold text-sm md:text-base transition ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 focus:outline-none focus:ring-4 focus:ring-teal-300"
          }`}
          aria-disabled={loading || !selectedFile}
          aria-busy={loading}
        >
          {loading ? "Processing..." : "Diagnose"}
        </button>
      </div>

      {/* Result Section - Right Side */}
      {!loading && result && (
        <div className="w-full md:w-1/2 max-w-sm md:max-w-md">
          <section
            className={`${diagnosisStatus.bgColor} ${diagnosisStatus.textColor} rounded-lg p-6 text-left shadow-xl`}
            role="region"
            aria-live="polite"
            tabIndex={0}
          >
            <h2 className="text-xl md:text-2xl font-bold mb-2">
              {diagnosisStatus.text}
            </h2>

            {probability !== null && !isNonSmear && (
              <p className="mb-4 text-base md:text-lg font-medium">
                Confidence: {(probability * 100).toFixed(1)}%
              </p>
            )}

            <p className="mb-4 text-sm md:text-base whitespace-pre-wrap">
              {result}
            </p>

            {prescription && !isNonSmear && (
              <div className="bg-white border-l-4 border-teal-500 px-4 py-3 text-teal-700 font-semibold rounded-md shadow-sm text-sm">
                <span className="font-semibold">Prescription: </span>
                {prescription}
              </div>
            )}

            <p className="mt-4 text-xs text-gray-500 italic">
              *Consult healthcare professionals for diagnosis confirmation and
              treatment.*
            </p>
          </section>
        </div>
      )}
    </div>
  );
};

export default MalariaDiagnosis;
