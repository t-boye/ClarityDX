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

const PHYSIOLOGICAL_RANGES = {
  age: { min: 18, max: 120 },
  trestbps: { min: 70, max: 200 },
  chol: { min: 100, max: 400 },
  thalach: { min: 60, max: 220 },
  oldpeak: { min: 0, max: 7 },
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
    if (["age", "trestbps", "chol", "thalach", "oldpeak"].includes(name)) {
      if (value !== "" && !/^\d*\.?\d*$/.test(value)) return;
    }
    setFormData((prev) => ({ ...prev, [name]: value }));
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
      if (formData[key] === "" || formData[key] === null) {
        errors[key] = `${
          formFieldGroups
            .flatMap((group) => group.fields)
            .find((field) => field.name === key)?.label || key
        } is required.`;
        continue;
      }

      if (numberFields.includes(key)) {
        const numValue = parseFloat(formData[key]);
        if (isNaN(numValue)) {
          errors[key] = `Must be a valid number`;
          continue;
        }

        if (numValue < 0 && key !== "oldpeak") {
          errors[key] = `Cannot be negative`;
          continue;
        }

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

      const response = await axios.post(
        `${BASE_API_URL}/predict/heart_disease`,
        apiData,
        {
          headers: { "Content-Type": "application/json" },
          timeout: 10000,
        }
      );

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

  // Mapping functions (unchanged)
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
          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm">{result.error}</p>
        </>
      );
    }

    let icon = (
      <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
    );
    if (
      result.diagnosis.toLowerCase().includes("likelihood") ||
      result.diagnosis.toLowerCase().includes("possible indication") ||
      result.prediction_class === 1
    ) {
      icon = (
        <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
      );
      if (result.prediction_class === 1) {
        icon = (
          <AlertCircle className="h-4 w-4 text-red-600 mt-0.5 flex-shrink-0" />
        );
      }
    }

    return (
      <>
        {icon}
        <div>
          <h3 className="font-semibold text-base">Diagnosis Result</h3>
          <p className="text-xs">{result.diagnosis}</p>
          {result.interpretation?.recommendation && (
            <p className="text-xs mt-1 font-medium">
              {result.interpretation.recommendation}
            </p>
          )}
          {result.probability !== undefined && (
            <p className="text-xs mt-1">
              Probability: {(result.probability * 100).toFixed(2)}%
            </p>
          )}
        </div>
      </>
    );
  };

  const formFieldGroups = [
    {
      title: "👤 Patient Information",
      fields: [
        { name: "age", label: "Age", type: "number", unit: "years" },
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
      title: "💓 Cardiac Symptoms",
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
          label: "Exercise Angina",
          type: "select",
          options: [
            { value: "No", label: "No" },
            { value: "Yes", label: "Yes" },
          ],
        },
      ],
    },
    {
      title: "📊 Vital Signs",
      fields: [
        {
          name: "trestbps",
          label: "Resting BP",
          type: "number",
          unit: "mm Hg",
        },
        {
          name: "thalach",
          label: "Max Heart Rate",
          type: "number",
          unit: "bpm",
        },
        {
          name: "oldpeak",
          label: "ST Depression",
          type: "number",
          unit: "mm",
          step: "0.1",
        },
      ],
    },
    {
      title: "💉 Blood Tests",
      fields: [
        { name: "chol", label: "Cholesterol", type: "number", unit: "mg/dL" },
        {
          name: "fbs",
          label: "Fasting BS > 120",
          type: "select",
          options: [
            { value: "No", label: "No" },
            { value: "Yes", label: "Yes" },
          ],
          unit: "mg/dL",
        },
      ],
    },
    {
      title: "📈 ECG & Imaging",
      fields: [
        {
          name: "restecg",
          label: "Resting ECG",
          type: "select",
          options: [
            { value: "Normal", label: "Normal" },
            { value: "ST-T Abnormality", label: "ST-T Abnormality" },
            { value: "LV Hypertrophy", label: "LV Hypertrophy" },
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
          label: "Major Vessels",
          type: "select",
          options: [
            { value: "0", label: "0" },
            { value: "1", label: "1" },
            { value: "2", label: "2" },
            { value: "3", label: "3" },
          ],
          unit: "fluoroscopy",
        },
      ],
    },
    {
      title: "🧬 Other Factors",
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
    <div className="min-h-screen bg-gray-50 py-4 px-4">
      <div className="max-w-5xl mx-auto">
        <Card className="shadow-lg overflow-hidden border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-red-600 to-red-700 p-4 text-white">
            <div className="flex items-center gap-3">
              <HeartPulse className="h-6 w-6" />
              <div>
                <h1 className="text-xl font-bold">
                  Heart Disease Risk Assessment
                </h1>
                <p className="text-sm text-red-100">
                  Enter cardiovascular metrics to assess heart disease risk
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-0">
            {/* Form Column */}
            <div className="lg:col-span-2 p-4 bg-white">
              <form onSubmit={handleSubmit} className="space-y-4">
                {formFieldGroups.map((group, groupIndex) => (
                  <div key={groupIndex} className="space-y-3">
                    <h3 className="font-semibold text-gray-800 text-sm uppercase tracking-wider flex items-center gap-2 border-b border-gray-100 pb-2">
                      {group.title}
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {group.fields.map((field) => (
                        <div key={field.name} className="space-y-1">
                          <div className="flex justify-between items-center">
                            <Label
                              htmlFor={field.name}
                              className="text-xs font-medium text-gray-700"
                            >
                              <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded-md">
                                {field.label}
                              </span>
                            </Label>
                            {field.unit && (
                              <span className="text-xs text-gray-500">
                                {field.unit}
                              </span>
                            )}
                          </div>
                          {field.type === "select" ? (
                            <Select
                              onValueChange={(value) =>
                                handleSelectChange(field.name, value)
                              }
                              value={formData[field.name]}
                            >
                              <SelectTrigger
                                className={`text-xs h-8 ${
                                  validationErrors[field.name]
                                    ? "border-red-500"
                                    : ""
                                }`}
                              >
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {field.options.map((option) => (
                                  <SelectItem
                                    key={option.value}
                                    value={option.value}
                                    className="text-xs"
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
                              className={`text-xs h-8 ${
                                validationErrors[field.name]
                                  ? "border-red-500"
                                  : ""
                              }`}
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
                  className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white py-2 text-sm shadow-md"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg
                        className="animate-spin h-4 w-4 text-white"
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
                    <span className="flex items-center justify-center gap-2">
                      <HeartPulse className="h-4 w-4" />
                      Assess Heart Risk
                    </span>
                  )}
                </Button>
              </form>
            </div>

            {/* Results Column */}
            <div className="bg-gray-50 p-4 border-l border-gray-200">
              <div className="space-y-4">
                <h2 className="text-base font-bold text-gray-800 flex items-center gap-2">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                  </svg>
                  Assessment Results
                </h2>

                {error && (
                  <Alert variant="destructive" className="text-xs">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {result ? (
                  <div className="space-y-3">
                    <div
                      className={`p-3 rounded-lg border ${
                        result.error
                          ? "bg-red-50 border-red-200"
                          : result.prediction_class === 1
                          ? "bg-red-50 border-red-200"
                          : "bg-green-50 border-green-200"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {getDiagnosisMessage(result)}
                      </div>
                    </div>

                    <Card className="bg-blue-50 border-blue-200">
                      <CardContent className="p-3">
                        <h3 className="text-sm font-medium text-blue-800 mb-2 flex items-center gap-2">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="16"
                            height="16"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="16" x2="12" y2="12"></line>
                            <line x1="12" y1="8" x2="12.01" y2="8"></line>
                          </svg>
                          Heart Health Guidance
                        </h3>
                        <ul className="text-xs text-blue-700 space-y-1">
                          <li className="flex items-start gap-2">
                            <span className="text-blue-500">•</span>
                            Optimal BP: &lt;120/80 mm Hg
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-blue-500">•</span>
                            Healthy cholesterol: &lt;200 mg/dL
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-blue-500">•</span>
                            Target heart rate: 60-100 bpm (resting)
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-blue-500">•</span>
                            ST depression &gt;1mm may indicate ischemia
                          </li>
                        </ul>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-6 text-center">
                    <div className="w-16 h-16 mb-3 rounded-full bg-gray-100 flex items-center justify-center">
                      <HeartPulse className="h-6 w-6 text-gray-400" />
                    </div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">
                      No results yet
                    </h3>
                    <p className="text-xs text-gray-500">
                      Submit your information for assessment
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
