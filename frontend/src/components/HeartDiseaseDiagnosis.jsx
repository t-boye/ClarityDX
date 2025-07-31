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
    <div className="min-h-screen bg-gray-50 py-4 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-4">
          <div className="flex items-center justify-center gap-2">
            <HeartPulse className="h-6 w-6 text-red-500" />
            <h1 className="text-xl font-bold text-gray-800">
              Heart Disease Risk Assessment
            </h1>
          </div>
          <p className="text-gray-600 text-sm max-w-md mx-auto mt-1">
            Enter your cardiovascular health metrics to assess your risk
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Form Column */}
          <div className="lg:col-span-2">
            <Card className="shadow-sm">
              <CardContent className="p-4">
                <form onSubmit={handleSubmit} className="space-y-4">
                  {formFieldGroups.map((group, groupIndex) => (
                    <div key={groupIndex} className="space-y-2">
                      <h3 className="text-base font-semibold text-gray-700 border-b pb-1">
                        {group.title}
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {group.fields.map((field) => (
                          <div key={field.name} className="space-y-1">
                            <Label htmlFor={field.name} className="text-xs">
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
                    className="w-full h-9 text-sm"
                  >
                    {loading ? (
                      <span className="flex items-center justify-center">
                        <svg
                          className="animate-spin -ml-1 mr-2 h-3 w-3 text-white"
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
                      "Assess Risk"
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Results Column */}
          <div className="space-y-3">
            <Card className="shadow-sm">
              <CardContent className="p-4">
                <h2 className="text-base font-bold text-gray-800 mb-2">
                  Assessment Results
                </h2>

                {error && (
                  <Alert variant="destructive" className="mb-3 p-2">
                    <AlertCircle className="h-3 w-3" />
                    <AlertTitle className="text-xs">Error</AlertTitle>
                    <AlertDescription className="text-xs">
                      {error}
                    </AlertDescription>
                  </Alert>
                )}

                {result ? (
                  <div className="space-y-3">
                    <div
                      className={`p-2 rounded border text-xs ${
                        result.error
                          ? "bg-red-50 border-red-200"
                          : result.prediction_class === 1
                          ? "bg-red-50 border-red-200"
                          : "bg-green-50 border-green-200"
                      }`}
                    >
                      <div className="flex items-start gap-2">
                        {getDiagnosisMessage(result)}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-4 text-center">
                    <div className="w-16 h-16 mb-2 rounded-full bg-gray-100 flex items-center justify-center">
                      <HeartPulse className="h-5 w-5 text-gray-400" />
                    </div>
                    <h3 className="text-sm font-medium text-gray-700 mb-1">
                      No results yet
                    </h3>
                    <p className="text-gray-500 text-xs">
                      Submit your information for assessment
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tips Card */}
            <Card className="shadow-sm bg-red-50 border-red-100">
              <CardContent className="p-3">
                <h3 className="font-semibold text-xs text-red-800 mb-1">
                  Heart Health Tips
                </h3>
                <ul className="space-y-1 text-xs text-red-700">
                  <li>• Maintain a healthy diet</li>
                  <li>• Exercise regularly</li>
                  <li>• Monitor blood pressure</li>
                  <li>• Control cholesterol</li>
                  <li>• Avoid smoking</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
