import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Select, {
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import axios from "axios";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  HeartPulse,
} from "lucide-react";
import { BASE_API_URL } from "../utils/apiConfig";

// Define physiological ranges for validation
const PHYSIOLOGICAL_RANGES = {
  age: { min: 18, max: 120 },
  trestbps: { min: 70, max: 200 }, // Resting BP (mm Hg)
  chol: { min: 100, max: 400 }, // Cholesterol (mg/dL)
  thalach: { min: 60, max: 220 }, // Max Heart Rate (bpm)
  oldpeak: { min: 0, max: 7 }, // ST Depression (mm)
};

export default function HeartDiseaseDiagnosis() {
  const [formData, setFormData] = useState({
    age: "",
    sex: "Male",
    cp: "Typical Angina",
    trestbps: "",
    chol: "",
    fbs: "No",
    restecg: "Normal",
    thalach: "",
    exang: "No",
    oldpeak: "",
    slope: "Upsloping",
    ca: "0",
    thal: "Normal",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;

    // Validate numeric fields as user types
    if (["age", "trestbps", "chol", "thalach", "oldpeak"].includes(name)) {
      // Allow empty string to clear the input, or valid number/decimal
      if (value !== "" && !/^\d*\.?\d*$/.test(value)) {
        return; // Only allow numbers and decimal points
      }
    }

    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleSelectChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear validation error for this field
    if (validationErrors[name]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const errors = {};
    const numberFields = ["age", "trestbps", "chol", "thalach", "oldpeak"];

    for (const key in formData) {
      // Check required fields (empty string or null)
      if (formData[key] === "" || formData[key] === null) {
        errors[key] = `${
          formFieldGroups
            .flatMap((group) => group.fields)
            .find((field) => field.name === key)?.label || key
        } is required.`;
        continue; // Move to the next field if required and empty
      }

      // Validate number fields for format and physiological ranges
      if (numberFields.includes(key)) {
        const numValue = parseFloat(formData[key]);

        if (isNaN(numValue)) {
          errors[key] = `Must be a valid number`;
          continue;
        }

        // oldpeak can be 0, but other fields should not be negative
        if (numValue < 0 && key !== "oldpeak") {
          errors[key] = `Cannot be negative`;
          continue;
        }

        // Check physiological ranges
        const range = PHYSIOLOGICAL_RANGES[key];
        if (range && (numValue < range.min || numValue > range.max)) {
          errors[key] = `Value must be between ${range.min} and ${range.max}`;
        }
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      setError("Please correct the errors in the form.");
      return;
    }

    setLoading(true);

    try {
      const apiData = {
        age: parseFloat(formData.age),
        sex: formData.sex === "Male" ? 1 : 0,
        cp: mapChestPain(formData.cp),
        trestbps: parseFloat(formData.trestbps),
        chol: parseFloat(formData.chol),
        fbs: formData.fbs === "Yes" ? 1 : 0,
        restecg: mapRestingECG(formData.restecg),
        thalach: parseFloat(formData.thalach),
        exang: formData.exang === "Yes" ? 1 : 0,
        oldpeak: parseFloat(formData.oldpeak),
        slope: mapSlope(formData.slope),
        ca: parseInt(formData.ca, 10),
        thal: mapThal(formData.thal),
      };

      // Re-validate all numeric values before sending, especially after parsing
      for (const [key, value] of Object.entries(apiData)) {
        if (typeof value === "number" && isNaN(value)) {
          throw new Error(`Invalid numeric value for ${key} after parsing.`);
        }
      }

      const response = await axios.post(
        `${BASE_API_URL}/predict/heart_disease`,
        apiData,
        {
          headers: { "Content-Type": "application/json" },
          timeout: 10000, // 10 second timeout
        }
      );

      if (response.status !== 200) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      setResult(response.data);
    } catch (err) {
      console.error("Heart Disease prediction error:", err);
      setError(
        err.response?.data?.details ||
          err.message ||
          "Failed to get diagnosis. Please try again."
      );
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  // Mapping functions remain the same...
  const mapChestPain = (cp) => {
    switch (cp) {
      case "Typical Angina":
        return 0;
      case "Atypical Angina":
        return 1;
      case "Non-anginal Pain":
        return 2;
      case "Asymptomatic":
        return 3;
      default:
        return 0;
    }
  };

  const mapRestingECG = (ecg) => {
    switch (ecg) {
      case "Normal":
        return 0;
      case "ST-T Wave Abnormality":
        return 1;
      case "Left Ventricular Hypertrophy":
        return 2;
      default:
        return 0;
    }
  };

  const mapSlope = (slope) => {
    switch (slope) {
      case "Upsloping":
        return 0;
      case "Flat":
        return 1;
      case "Downsloping":
        return 2;
      default:
        return 0;
    }
  };

  const mapThal = (thal) => {
    switch (thal) {
      case "Normal":
        return 2;
      case "Fixed Defect":
        return 1;
      case "Reversible Defect":
        return 3;
      default:
        return 2;
    }
  };

  const getDiagnosisMessage = (result) => {
    if (result.error) {
      return (
        <>
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm">{result.error}</p>
        </>
      );
    }

    let icon = (
      <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
    );
    if (
      result.diagnosis.toLowerCase().includes("likelihood") ||
      result.diagnosis.toLowerCase().includes("possible indication") ||
      result.prediction_class === 1 // Assuming 1 means positive for heart disease
    ) {
      icon = (
        <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
      );
      if (result.prediction_class === 1) {
        // More explicit check for high risk
        icon = (
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
        );
      }
    }

    return (
      <>
        {icon}
        <div>
          <h3 className="font-semibold text-lg">Diagnosis Result</h3>
          <p className="text-sm">{result.diagnosis}</p>
          {result.interpretation?.recommendation && (
            <p className="text-sm mt-1 font-medium">
              {result.interpretation.recommendation}
            </p>
          )}
          {result.probability !== undefined && (
            <p className="text-sm mt-1">
              Probability of Heart Disease:{" "}
              {(result.probability * 100).toFixed(2)}%
            </p>
          )}
        </div>
      </>
    );
  };

  const getRiskFactorMessage = (result) => {
    // This section seems to be designed for a more detailed interpretation from the backend.
    // If the backend doesn't provide `significant_risk_factors`, this will not display.
    // The current backend code does not produce this.
    return null; // Returning null as current backend doesn't provide this.
  };

  const getDisclaimer = (result) => {
    if (result.interpretation?.disclaimer) {
      return (
        <p className="text-xs italic text-gray-500 mt-4">
          {result.interpretation.disclaimer}
        </p>
      );
    }
    return null;
  };

  // Group form fields into categories
  const formFieldGroups = [
    {
      title: "Patient Information",
      fields: [
        { name: "age", label: "Age (years)", type: "number" },
        {
          name: "sex",
          label: "Sex",
          type: "select",
          options: [
            { value: "Male", label: "Male" },
            { value: "Female", label: "Female" },
          ],
        },
      ],
    },
    {
      title: "Cardiac Symptoms",
      fields: [
        {
          name: "cp",
          label: "Chest Pain Type",
          type: "select",
          options: [
            { value: "Typical Angina", label: "Typical Angina" },
            { value: "Atypical Angina", label: "Atypical Angina" },
            { value: "Non-anginal Pain", label: "Non-anginal Pain" },
            { value: "Asymptomatic", label: "Asymptomatic" },
          ],
        },
        {
          name: "exang",
          label: "Exercise Induced Angina",
          type: "select",
          options: [
            { value: "No", label: "No" },
            { value: "Yes", label: "Yes" },
          ],
        },
      ],
    },
    {
      title: "Vital Signs",
      fields: [
        { name: "trestbps", label: "Resting BP (mm Hg)", type: "number" },
        { name: "thalach", label: "Max Heart Rate (bpm)", type: "number" },
        {
          name: "oldpeak",
          label: "ST Depression (mm)",
          type: "number",
          step: "0.1",
        },
      ],
    },
    {
      title: "Blood Tests",
      fields: [
        { name: "chol", label: "Cholesterol (mg/dL)", type: "number" },
        {
          name: "fbs",
          label: "Fasting BS > 120 mg/dL",
          type: "select",
          options: [
            { value: "No", label: "No" },
            { value: "Yes", label: "Yes" },
          ],
        },
      ],
    },
    {
      title: "ECG & Imaging",
      fields: [
        {
          name: "restecg",
          label: "Resting ECG",
          type: "select",
          options: [
            { value: "Normal", label: "Normal" },
            { value: "ST-T Wave Abnormality", label: "ST-T Wave Abnormality" },
            { value: "Left Ventricular Hypertrophy", label: "LV Hypertrophy" },
          ],
        },
        {
          name: "slope",
          label: "ST Segment Slope",
          type: "select",
          options: [
            { value: "Upsloping", label: "Upsloping" },
            { value: "Flat", label: "Flat" },
            { value: "Downsloping", label: "Downsloping" },
          ],
        },
        {
          name: "ca",
          label: "Major Vessels (fluoroscopy)",
          type: "select",
          options: [
            { value: "0", label: "0" },
            { value: "1", label: "1" },
            { value: "2", label: "2" },
            { value: "3", label: "3" },
          ],
        },
      ],
    },
    {
      title: "Other Factors",
      fields: [
        {
          name: "thal",
          label: "Thalassemia",
          type: "select",
          options: [
            { value: "Normal", label: "Normal" },
            { value: "Fixed Defect", label: "Fixed Defect" },
            { value: "Reversible Defect", label: "Reversible Defect" },
          ],
        },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-red-50 py-8 px-4">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden -z-10">
        <div className="absolute top-0 left-0 w-32 h-32 rounded-full bg-blue-200 opacity-20 animate-float1"></div>
        <div className="absolute top-1/4 right-0 w-48 h-48 rounded-full bg-red-200 opacity-20 animate-float2"></div>
        <div className="absolute bottom-0 left-1/3 w-40 h-40 rounded-full bg-blue-100 opacity-15 animate-float3"></div>
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3">
            <HeartPulse className="h-10 w-10 text-red-500" />
            <h1 className="text-3xl font-bold text-gray-800">
              Heart Disease Risk Assessment
            </h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto mt-2">
            Enter your cardiovascular health metrics to assess your risk for
            heart disease
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column - Form */}
          <div className="lg:col-span-2">
            <Card className="shadow-lg border-0 rounded-xl overflow-hidden">
              <CardContent className="p-6">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {formFieldGroups.map((group, groupIndex) => (
                    <div key={groupIndex} className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-700 border-b pb-2">
                        {group.title}
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {group.fields.map((field) => (
                          <div key={field.name} className="space-y-2">
                            <Label
                              htmlFor={field.name}
                              className="text-gray-700"
                            >
                              {field.label}
                            </Label>
                            {field.type === "select" ? (
                              <Select
                                onValueChange={(value) =>
                                  handleSelectChange(field.name, value)
                                }
                                value={formData[field.name]}
                              >
                                <SelectTrigger
                                  id={field.name}
                                  className={`w-full ${
                                    validationErrors[field.name]
                                      ? "border-red-500"
                                      : ""
                                  }`}
                                >
                                  <SelectValue
                                    placeholder={`Select ${field.label}`}
                                  />
                                </SelectTrigger>
                                <SelectContent>
                                  {field.options.map((option) => (
                                    <SelectItem
                                      key={option.value}
                                      value={option.value}
                                    >
                                      {option.label}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            ) : (
                              <Input
                                id={field.name}
                                name={field.name}
                                type={field.type}
                                step={field.step || undefined}
                                value={formData[field.name]}
                                onChange={handleChange}
                                className={`w-full ${
                                  validationErrors[field.name]
                                    ? "border-red-500"
                                    : ""
                                }`}
                                placeholder={`Enter ${field.label}`}
                              />
                            )}
                            {validationErrors[field.name] && (
                              <p className="text-red-500 text-xs">
                                {validationErrors[field.name]}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}

                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full py-6 bg-gradient-to-r from-blue-500 to-teal-500 hover:from-blue-600 hover:to-teal-600 text-lg font-medium shadow-md"
                  >
                    {loading ? (
                      <span className="flex items-center justify-center">
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
                        Analyzing...
                      </span>
                    ) : (
                      "Assess Heart Disease Risk"
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Right column - Results */}
          <div className="space-y-6">
            <Card className="shadow-lg border-0 rounded-xl h-full">
              <CardContent className="p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                  Assessment Results
                </h2>

                {error && (
                  <Alert variant="destructive" className="mb-6">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {result ? (
                  <div className="space-y-6">
                    <div
                      className={`p-4 rounded-lg border ${
                        result.error
                          ? "bg-red-50 border-red-200"
                          : result.prediction_class === 1 // Use prediction_class for color logic
                          ? "bg-red-50 border-red-200"
                          : "bg-green-50 border-green-200"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {getDiagnosisMessage(result)}
                      </div>
                    </div>

                    {getRiskFactorMessage(result)}
                    {getDisclaimer(result)}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="w-24 h-24 mb-4 rounded-full bg-gray-100 flex items-center justify-center">
                      <HeartPulse className="h-10 w-10 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">
                      No results yet
                    </h3>
                    <p className="text-gray-500 text-sm max-w-xs">
                      Submit your cardiovascular information to receive a heart
                      disease risk assessment.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Heart health tips card */}
            <Card className="shadow-lg border-0 rounded-xl bg-red-50 border-red-100">
              <CardContent className="p-6">
                <h3 className="font-semibold text-red-800 mb-3">
                  Heart Health Tips
                </h3>
                <ul className="space-y-2 text-sm text-red-700">
                  <li className="flex items-start gap-2">
                    <span>•</span> Maintain a healthy diet low in saturated fats
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Exercise for at least 30 minutes most days
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Monitor and control blood pressure
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Keep cholesterol levels in check
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Avoid smoking and limit alcohol consumption
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Manage stress through relaxation techniques
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Add CSS for animated floating elements */}
      <style jsx>{`
        @keyframes float1 {
          0%,
          100% {
            transform: translate(0, 0) rotate(0deg);
          }
          50% {
            transform: translate(20px, 30px) rotate(5deg);
          }
        }
        @keyframes float2 {
          0%,
          100% {
            transform: translate(0, 0) rotate(0deg);
          }
          50% {
            transform: translate(-30px, 20px) rotate(-5deg);
          }
        }
        @keyframes float3 {
          0%,
          100% {
            transform: translate(0, 0) rotate(0deg);
          }
          50% {
            transform: translate(15px, -20px) rotate(3deg);
          }
        }
        .animate-float1 {
          animation: float1 10s ease-in-out infinite;
        }
        .animate-float2 {
          animation: float2 12s ease-in-out infinite;
        }
        .animate-float3 {
          animation: float3 14s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
