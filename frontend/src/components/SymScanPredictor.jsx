import React, { useState, useRef, useEffect } from "react";
import { SYMPTOM_SUGGESTIONS } from "../utils/suggest.js";

const API_BASE_URL =
  import.meta.env.VITE_APP_API_URL || "http://localhost:8000";

function SymScanPredictor() {
  const [symptomsInput, setSymptomsInput] = useState("");
  const [symptoms, setSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);

  const [filteredSuggestions, setFilteredSuggestions] = useState([]);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  const liveRegionRef = useRef();
  const inputRef = useRef();

  // Announce loading and errors via ARIA live region
  useEffect(() => {
    if (liveRegionRef.current) {
      if (loading) {
        liveRegionRef.current.textContent = "Analyzing symptoms...";
      } else if (error) {
        liveRegionRef.current.textContent = `Error: ${error}`;
      } else {
        liveRegionRef.current.textContent = "";
      }
    }
  }, [loading, error]);

  // Filter suggestions on input change
  useEffect(() => {
    const input = symptomsInput.trim().toLowerCase();
    if (input.length > 0) {
      const filtered = SYMPTOM_SUGGESTIONS.filter(
        (sym) => sym.includes(input) && !symptoms.includes(sym)
      );
      setFilteredSuggestions(filtered);
      setActiveSuggestionIndex(-1);
    } else {
      setFilteredSuggestions([]);
      setActiveSuggestionIndex(-1);
    }
  }, [symptomsInput, symptoms]);

  // Add symptom helper
  const addSymptom = (symptom) => {
    const normalized = symptom.toLowerCase();
    if (normalized && !symptoms.includes(normalized)) {
      setSymptoms([...symptoms, normalized]);
    }
    setSymptomsInput("");
    setFilteredSuggestions([]);
    setActiveSuggestionIndex(-1);
  };

  // Input handlers
  const handleInputChange = (e) => {
    setSymptomsInput(e.target.value);
    setError(null);
  };

  const handleKeyDown = (e) => {
    if ((e.key === "Enter" || e.key === ",") && symptomsInput.trim() !== "") {
      e.preventDefault();
      if (activeSuggestionIndex >= 0) {
        addSymptom(filteredSuggestions[activeSuggestionIndex]);
      } else {
        addSymptom(symptomsInput.trim());
      }
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (filteredSuggestions.length > 0) {
        setActiveSuggestionIndex((prev) =>
          prev + 1 < filteredSuggestions.length ? prev + 1 : 0
        );
      }
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (filteredSuggestions.length > 0) {
        setActiveSuggestionIndex((prev) =>
          prev - 1 >= 0 ? prev - 1 : filteredSuggestions.length - 1
        );
      }
    } else if (e.key === "Escape") {
      setFilteredSuggestions([]);
      setActiveSuggestionIndex(-1);
    }
  };

  const removeSymptom = (symptomToRemove) => {
    setSymptoms(symptoms.filter((sym) => sym !== symptomToRemove));
  };

  const clearSymptoms = () => {
    setSymptoms([]);
    setSymptomsInput("");
    setError(null);
    setPredictionResult(null);
    setFilteredSuggestions([]);
    setActiveSuggestionIndex(-1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setPredictionResult(null);

    if (symptoms.length === 0) {
      setError("Please enter at least one symptom.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/predict/symscan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "An unknown error occurred on the server.");
        setPredictionResult(data);
      } else {
        setPredictionResult(data);
      }
    } catch (err) {
      setError(
        "Failed to connect to the server. Please ensure the backend is running and accessible."
      );
    } finally {
      setLoading(false);
    }
  };

  const ConfidenceBadge = ({ confidence }) => {
    let colorClass = "bg-yellow-400 text-yellow-900";
    if (confidence.endsWith("%")) {
      const percent = parseInt(confidence);
      if (percent >= 80) colorClass = "bg-green-500 text-white";
      else if (percent < 50) colorClass = "bg-red-500 text-white";
    }
    return (
      <span
        className={`inline-block px-2 py-1 text-xs font-semibold rounded ${colorClass}`}
        aria-label={`Confidence ${confidence}`}
        title={`Confidence ${confidence}`}
      >
        {confidence}
      </span>
    );
  };

  return (
    // Updated container to use `max-w-4xl` for a smaller overall footprint
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 p-6 flex flex-col lg:flex-row lg:items-start lg:justify-center">
      {/* Input Section - using `max-w-md` for a more compact form */}
      <div className="bg-white p-8 rounded-xl shadow-2xl w-full lg:w-1/2 max-w-md lg:mr-8 mb-8 lg:mb-0">
        <h2 className="text-3xl font-extrabold text-gray-900 mb-6 text-center lg:text-left">
          Sym<span className="text-indigo-600">Scan</span> Diagnosis
        </h2>
        <p className="text-gray-600 mb-6 text-center lg:text-left leading-relaxed text-sm">
          Enter your symptoms below, adding one at a time (press Enter or
          comma). Click a symptom tag to remove it or select from suggestions.
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-4"
          aria-describedby="live-region"
        >
          <label
            htmlFor="symptoms-input"
            className="block text-sm font-medium text-gray-800"
          >
            Your Symptoms
          </label>

          <div
            className="flex flex-wrap gap-2 mb-2 min-h-[40px]"
            aria-live="polite"
            aria-relevant="additions removals"
          >
            {symptoms.length === 0 && (
              <p className="text-gray-400 italic text-sm">
                No symptoms added yet.
              </p>
            )}
            {symptoms.map((symptom) => (
              <button
                key={symptom}
                type="button"
                onClick={() => removeSymptom(symptom)}
                className="bg-indigo-600 text-white px-2 py-1 rounded-full text-xs shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                aria-label={`Remove symptom ${symptom}`}
                title="Click to remove"
              >
                {symptom} ×
              </button>
            ))}
          </div>

          <div className="relative">
            <input
              type="text"
              id="symptoms-input"
              value={symptomsInput}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Type symptom and press Enter or comma"
              className="block w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              disabled={loading}
              aria-describedby="symptoms-help"
              aria-autocomplete="list"
              aria-haspopup="listbox"
              aria-expanded={filteredSuggestions.length > 0}
              autoComplete="off"
              ref={inputRef}
            />

            {filteredSuggestions.length > 0 && (
              <ul
                className="absolute z-10 max-h-48 w-full overflow-auto rounded-md bg-white border border-gray-300 shadow-lg"
                role="listbox"
                aria-label="Symptom suggestions"
              >
                {filteredSuggestions.map((suggestion, index) => (
                  <li
                    key={suggestion}
                    role="option"
                    aria-selected={index === activeSuggestionIndex}
                    className={`cursor-pointer px-3 py-2 text-sm ${
                      index === activeSuggestionIndex
                        ? "bg-indigo-600 text-white"
                        : "text-gray-700"
                    } hover:bg-indigo-500 hover:text-white`}
                    onMouseDown={(e) => {
                      e.preventDefault();
                      addSymptom(suggestion);
                    }}
                  >
                    {suggestion}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <p id="symptoms-help" className="text-gray-500 text-xs">
            Add symptoms one by one. Remove any by clicking on them.
          </p>

          {symptoms.length > 0 && (
            <button
              type="button"
              onClick={clearSymptoms}
              className="text-xs text-red-600 hover:text-red-800 focus:outline-none"
            >
              Clear All Symptoms
            </button>
          )}

          <button
            type="submit"
            className="w-full flex justify-center py-2 px-3 border border-transparent rounded-lg shadow-md text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? (
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            ) : (
              "Get Diagnosis"
            )}
          </button>

          <div
            aria-live="polite"
            aria-atomic="true"
            className="sr-only"
            ref={liveRegionRef}
            id="live-region"
          ></div>
        </form>
      </div>

      {/* Result Section - using `max-w-md` for consistency */}
      <div className="bg-white p-8 rounded-xl shadow-2xl w-full lg:w-1/2 max-w-md">
        {error && (
          <div
            className="p-4 bg-red-50 border border-red-300 text-red-800 rounded-lg text-xs transition-all duration-300 ease-in-out"
            role="alert"
            aria-live="assertive"
          >
            <p className="font-bold mb-1">Diagnosis Error:</p>
            <p>{error}</p>
          </div>
        )}

        {!predictionResult && !error && !loading && (
          <div className="p-6 text-center text-gray-500">
            <svg
              className="mx-auto h-10 w-10 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              ></path>
            </svg>
            <p className="mt-2 text-base">
              Your diagnosis results will appear here.
            </p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center p-6 text-indigo-600">
            <svg
              className="animate-spin h-8 w-8 text-indigo-600 mb-2"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <p className="text-base font-semibold">Analyzing symptoms...</p>
          </div>
        )}

        {predictionResult && (
          <div className="transition-all duration-300 ease-in-out text-sm">
            {predictionResult.error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-md text-xs">
                <p className="font-semibold mb-1">Backend Reported Error:</p>
                <p>{predictionResult.error}</p>
                {predictionResult.details && (
                  <pre className="text-xs mt-1 whitespace-pre-wrap">
                    Details: {JSON.stringify(predictionResult.details, null, 2)}
                  </pre>
                )}
              </div>
            )}

            <p className="mb-3 text-xl font-extrabold text-indigo-700">
              Predicted Primary Disease:{" "}
              <span className="text-black">
                {predictionResult.predicted_disease || "N/A"}
              </span>{" "}
              {predictionResult.confidence_for_primary_prediction &&
                predictionResult.confidence_for_primary_prediction !==
                  "N/A" && (
                  <ConfidenceBadge
                    confidence={
                      predictionResult.confidence_for_primary_prediction
                    }
                  />
                )}
            </p>

            {predictionResult.top_n_predictions &&
              predictionResult.top_n_predictions.length > 0 && (
                <div className="mt-4 border-t border-gray-200 pt-4">
                  <h4 className="font-bold text-gray-800 text-base mb-2">
                    Other Top Possibilities:
                  </h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-700 max-h-36 overflow-auto">
                    {predictionResult.top_n_predictions.map((p, index) => (
                      <li key={index} className="text-sm">
                        <span className="font-semibold">{p.disease}</span>{" "}
                        (Confidence: {p.confidence})
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {predictionResult.precautions &&
              predictionResult.precautions.length > 0 && (
                <div className="mt-4 border-t border-gray-200 pt-4">
                  <h4 className="font-bold text-gray-800 text-base mb-2">
                    Recommended Precautions:
                  </h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-700">
                    {predictionResult.precautions.map((p, index) => (
                      <li key={index} className="text-sm">
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

            {predictionResult.normalized_symptoms_used_by_model &&
              predictionResult.normalized_symptoms_used_by_model.length > 0 && (
                <div className="mt-4 border-t border-gray-200 pt-4">
                  <h4 className="font-bold text-gray-800 text-base mb-2">
                    Symptoms Used by Model:
                  </h4>
                  <p className="text-xs text-gray-700">
                    {predictionResult.normalized_symptoms_used_by_model.join(
                      ", "
                    )}
                  </p>
                </div>
              )}

            {predictionResult.unrecognized_symptoms &&
              predictionResult.unrecognized_symptoms.length > 0 && (
                <div
                  className="mt-6 p-3 bg-yellow-50 border border-yellow-300 rounded-lg text-xs text-yellow-800"
                  role="note"
                  aria-live="polite"
                >
                  <p className="font-bold mb-1">
                    Note: Some Symptoms Were Unrecognized
                  </p>
                  <ul className="list-disc list-inside">
                    {predictionResult.unrecognized_symptoms.map((s, index) => (
                      <li
                        key={index}
                        title={`The symptom "${s}" was not recognized by the model and was omitted from analysis.`}
                      >
                        {s}
                      </li>
                    ))}
                  </ul>
                  <p className="mt-2 text-xs">
                    These symptoms could not be mapped to the model's vocabulary
                    and were not used in the diagnosis.
                  </p>
                </div>
              )}

            <p className="mt-6 text-xs text-gray-500 italic text-center leading-relaxed">
              <span className="font-semibold">Disclaimer:</span>{" "}
              {predictionResult.medical_disclaimer ||
                "This system is informational only and not a substitute for professional medical advice. Always consult a qualified healthcare provider."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default SymScanPredictor;
