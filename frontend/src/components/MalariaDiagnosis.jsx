import React, { useState } from "react";
import { Dialog, DialogPanel } from "@headlessui/react";
import { BASE_API_URL } from "../utils/apiConfig";

const MalariaDiagnosis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [probability, setProbability] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isNonSmear, setIsNonSmear] = useState(false);

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
    setIsNonSmear(false);

    const formData = new FormData();
    formData.append("image", selectedFile);

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

      if (data && data.diagnosis) {
        setResult(data.diagnosis);
        setProbability(data.probability);
        setIsNonSmear(data.isNonSmear);
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
    <div className="min-h-screen flex items-center justify-center px-4 py-8 bg-gradient-to-br from-blue-50 to-green-50">
      <div className="bg-white/80 backdrop-blur-md p-8 rounded-2xl shadow-2xl w-full max-w-md text-center transition-transform duration-300 hover:scale-[1.01]">
        <h2 className="text-3xl font-bold text-gray-800 mb-3">
          🦠 Malaria Diagnosis
        </h2>
        <p className="text-gray-600 mb-6">
          Upload your blood smear image to check for Malaria.
        </p>

        <input
          type="file"
          accept="image/*"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 text-sm"
          onChange={handleFileChange}
        />

        <button
          onClick={handleSubmit}
          className={`w-full py-2 rounded-lg text-white font-medium transition-colors duration-300 ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600"
          }`}
          disabled={loading}
        >
          {loading ? "Processing..." : "Submit"}
        </button>

        {loading && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg animate-pulse">
              <p className="text-gray-700 font-medium">
                Processing Diagnosis...
              </p>
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
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
        >
          <DialogPanel className="bg-white w-full max-w-md p-6 rounded-lg shadow-lg animate-fade-in">
            <h3 className="text-xl font-semibold text-gray-800">
              Diagnosis Result
            </h3>
            {probability !== null && (
              <p className="mt-2 text-gray-700">
                Probability: {probability.toFixed(2)}
              </p>
            )}
            {isNonSmear && (
              <p className="mt-2 text-red-600 font-medium">
                This image is not a blood smear. Please upload a valid image.
              </p>
            )}
            <p className="mt-4 text-gray-700">{result}</p>

            <p className="mt-4 text-xs text-gray-500">
              **Disclaimer:** The information provided is for educational
              purposes only and should not replace professional medical advice.
              Always consult a licensed healthcare provider.
            </p>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => {
                  setResult(null);
                  setProbability(null);
                  setIsNonSmear(false);
                }}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
              >
                Close
              </button>
              <a
                href="/info"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Learn More
              </a>
            </div>
          </DialogPanel>
        </Dialog>
      </div>

      {/* Animated gradient background */}
      <style jsx>{`
        .animate-gradient {
          background-size: 400% 400%;
          animation: gradientBG 15s ease infinite;
        }

        @keyframes gradientBG {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }

        .animate-fade-in {
          animation: fadeIn 0.5s ease-out forwards;
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default MalariaDiagnosis;
