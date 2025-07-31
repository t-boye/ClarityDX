import React, { useState, useEffect } from "react";
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
  FlaskConical,
  FileText,
  HeartPulse,
} from "lucide-react";
import { BASE_API_URL } from "../utils/apiConfig";

export default function KidneyDiseaseDiagnosis({ onDiagnosis }) {
  const [formData, setFormData] = useState({
    "Age (yrs)": "",
    "Blood Pressure (mm/Hg)": "",
    "Specific Gravity": "",
    Albumin: "",
    Sugar: "",
    "Blood Glucose Random (mgs/dL)": "",
    "Blood Urea (mgs/dL)": "",
    "Serum Creatinine (mgs/dL)": "",
    "Sodium (mEq/L)": "",
    "Potassium (mEq/L)": "",
    "Hemoglobin (gms)": "",
    "Packed Cell Volume": "",
    "White Blood Cells (cells/cmm)": "",
    "Red Blood Cells (millions/cmm)": "",
    "Red Blood Cells: normal": "normal",
    "Pus Cells: normal": "normal",
    "Pus Cell Clumps: present": "not present",
    "Bacteria: present": "not present",
    "Hypertension: yes": "no",
    "Diabetes Mellitus: yes": "no",
    "Coronary Artery Disease: yes": "no",
    "Appetite: poor": "good",
    "Pedal Edema: yes": "no",
    "Anemia: yes": "no",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isFormValid, setIsFormValid] = useState(false);

  const selectOptions = {
    "Red Blood Cells: normal": ["normal", "abnormal"],
    "Pus Cells: normal": ["normal", "abnormal"],
    "Pus Cell Clumps: present": ["not present", "present"],
    "Bacteria: present": ["not present", "present"],
    "Hypertension: yes": ["no", "yes"],
    "Diabetes Mellitus: yes": ["no", "yes"],
    "Coronary Artery Disease: yes": ["no", "yes"],
    "Appetite: poor": ["good", "poor"],
    "Pedal Edema: yes": ["no", "yes"],
    "Anemia: yes": ["no", "yes"],
  };

  useEffect(() => {
    const numericFields = Object.keys(formData).filter(
      (key) => !selectOptions[key]
    );
    const allNumericFieldsFilled = numericFields.every(
      (key) => formData[key] !== "" && !isNaN(Number(formData[key]))
    );
    setIsFormValid(allNumericFieldsFilled);
  }, [formData, selectOptions]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSelectChange = (name, value) => {
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isFormValid) {
      setError("Please fill in all the numeric fields before submitting.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiData = {
        ...formData,
        ...Object.fromEntries(
          Object.entries(formData).map(([key, value]) => {
            if (selectOptions[key]) {
              return [
                key,
                value === "yes" || value === "normal" || value === "present"
                  ? 1
                  : 0,
              ];
            } else {
              return [key, parseFloat(value)];
            }
          })
        ),
      };

      const response = await axios.post(
        `${BASE_API_URL}/predict/ckd`,
        apiData,
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      setResult(response.data);
      if (onDiagnosis) {
        onDiagnosis(response.data);
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(
          err.response?.data?.error ||
            err.response?.data?.response?.message ||
            "An error occurred while communicating with the server."
        );
        console.error("Axios error:", err.response?.data || err.message);
      } else {
        setError("Failed to connect to the server.");
        console.error("Non-Axios error:", err);
      }
    } finally {
      setLoading(false);
    }
  };

  const getDiagnosisMessage = (res) => {
    if (res.error) {
      return (
        <div className="flex items-start gap-4">
          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm">{res.error}</p>
        </div>
      );
    }

    const diagnosisText =
      res.diagnosis ||
      (res.class_names && res.prediction !== undefined
        ? res.class_names[res.prediction]
        : null) ||
      "No diagnosis provided.";

    const isCKD = diagnosisText?.toLowerCase().includes("ckd");
    const icon = isCKD ? (
      <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
    ) : (
      <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
    );

    return (
      <div className="flex items-start gap-4">
        {icon}
        <div>
          <h3 className="font-semibold text-lg">Diagnosis Result</h3>
          <p className="text-sm">{diagnosisText}</p>
        </div>
      </div>
    );
  };

  const getExplanation = (res) => {
    if (res.explanation) {
      const explanation = res.explanation;
      return (
        <div className="bg-white p-6 rounded-xl border shadow-sm">
          <h4 className="font-semibold text-gray-800 text-lg mb-3 flex items-center gap-2">
            <FileText className="h-5 w-5 text-blue-500" />
            Detailed Analysis
          </h4>
          <div className="space-y-4 text-sm text-gray-700">
            {explanation.overall_assessment && (
              <div>
                <h5 className="font-bold">Overall Assessment:</h5>
                <p>{explanation.overall_assessment}</p>
              </div>
            )}
            {explanation.probability_ckd !== undefined && (
              <div>
                <h5 className="font-bold">Probability of CKD:</h5>
                <p className="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                  {(explanation.probability_ckd * 100).toFixed(2)}%
                </p>
              </div>
            )}
            {explanation.significant_risk_factors?.factors?.length > 0 && (
              <div>
                <h5 className="font-bold">
                  {explanation.significant_risk_factors.message}
                </h5>
                <ul className="list-disc pl-5 space-y-1">
                  {explanation.significant_risk_factors.factors.map(
                    (factor, index) => (
                      <li key={index}>{factor}</li>
                    )
                  )}
                </ul>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  const getDisclaimer = (res) => {
    if (res.explanation && res.explanation.disclaimer) {
      return (
        <p className="text-xs italic text-gray-500 mt-4 text-center">
          {res.explanation.disclaimer}
        </p>
      );
    }
    return null;
  };

  const formFieldGroups = [
    {
      title: "Patient Information",
      icon: <FlaskConical className="h-5 w-5" />,
      fields: [
        { label: "Age", name: "Age (yrs)", unit: "years" },
        {
          label: "Blood Pressure",
          name: "Blood Pressure (mm/Hg)",
          unit: "mm/Hg",
        },
        { label: "Specific Gravity", name: "Specific Gravity" },
        { label: "Albumin", name: "Albumin" },
        { label: "Sugar", name: "Sugar" },
      ],
    },
    {
      title: "Blood Test Results",
      icon: <HeartPulse className="h-5 w-5" />,
      fields: [
        {
          label: "Blood Glucose Random",
          name: "Blood Glucose Random (mgs/dL)",
          unit: "mgs/dL",
        },
        { label: "Blood Urea", name: "Blood Urea (mgs/dL)", unit: "mgs/dL" },
        {
          label: "Serum Creatinine",
          name: "Serum Creatinine (mgs/dL)",
          unit: "mgs/dL",
        },
        { label: "Sodium", name: "Sodium (mEq/L)", unit: "mEq/L" },
        { label: "Potassium", name: "Potassium (mEq/L)", unit: "mEq/L" },
        { label: "Hemoglobin", name: "Hemoglobin (gms)", unit: "gms" },
        { label: "Packed Cell Volume", name: "Packed Cell Volume" },
        {
          label: "White Blood Cells",
          name: "White Blood Cells (cells/cmm)",
          unit: "cells/cmm",
        },
        {
          label: "Red Blood Cells",
          name: "Red Blood Cells (millions/cmm)",
          unit: "millions/cmm",
        },
      ],
    },
    {
      title: "Clinical Observations",
      icon: <FileText className="h-5 w-5" />,
      fields: [
        { label: "Red Blood Cells", name: "Red Blood Cells: normal" },
        { label: "Pus Cells", name: "Pus Cells: normal" },
        { label: "Pus Cell Clumps", name: "Pus Cell Clumps: present" },
        { label: "Bacteria", name: "Bacteria: present" },
        { label: "Hypertension", name: "Hypertension: yes" },
        { label: "Diabetes Mellitus", name: "Diabetes Mellitus: yes" },
        {
          label: "Coronary Artery Disease",
          name: "Coronary Artery Disease: yes",
        },
        { label: "Appetite", name: "Appetite: poor" },
        { label: "Pedal Edema", name: "Pedal Edema: yes" },
        { label: "Anemia", name: "Anemia: yes" },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 py-8 px-4">
      {/* Improved animated background elements */}
      <div className="fixed inset-0 overflow-hidden -z-10">
        <div className="absolute top-0 left-0 w-32 h-32 rounded-full bg-blue-200 opacity-10 animate-float1"></div>
        <div className="absolute top-1/4 right-0 w-48 h-48 rounded-full bg-green-200 opacity-10 animate-float2"></div>
        <div className="absolute bottom-0 left-1/3 w-40 h-40 rounded-full bg-blue-100 opacity-10 animate-float3"></div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-4 leading-tight">
            Kidney Health Assessment
          </h1>
          <p className="text-lg md:text-xl text-gray-500 max-w-3xl mx-auto">
            Enter your health metrics below to receive a precise evaluation of
            your kidney function and overall renal health.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Left column - Form */}
          <div className="lg:col-span-3">
            <Card className="shadow-xl border-0 rounded-2xl overflow-hidden bg-white/90 backdrop-blur-sm">
              <CardContent className="p-8">
                <form onSubmit={handleSubmit} className="space-y-8">
                  {formFieldGroups.map((group, groupIndex) => (
                    <div key={groupIndex} className="space-y-6">
                      <div className="flex items-center gap-3 border-b pb-3 border-gray-200">
                        {group.icon}
                        <h3 className="text-xl font-semibold text-gray-800">
                          {group.title}
                        </h3>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {group.fields.map((field) => (
                          <div key={field.name} className="space-y-2">
                            <Label
                              htmlFor={field.name}
                              className="text-gray-700 font-medium flex justify-between items-center"
                            >
                              <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-md">
                                {field.label}
                              </span>
                              {field.unit && (
                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                                  {field.unit}
                                </span>
                              )}
                            </Label>
                            {selectOptions[field.name] ? (
                              <Select
                                onValueChange={(value) =>
                                  handleSelectChange(field.name, value)
                                }
                                defaultValue={formData[field.name]}
                              >
                                <SelectTrigger
                                  id={field.name}
                                  className="w-full h-12"
                                >
                                  <SelectValue
                                    placeholder={`Select ${field.label}`}
                                  />
                                </SelectTrigger>
                                <SelectContent>
                                  {selectOptions[field.name].map((option) => (
                                    <SelectItem
                                      key={option}
                                      value={option}
                                      className="hover:bg-gray-50"
                                    >
                                      {option.charAt(0).toUpperCase() +
                                        option.slice(1)}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            ) : (
                              <Input
                                id={field.name}
                                name={field.name}
                                type="number"
                                step="any"
                                value={formData[field.name]}
                                onChange={handleChange}
                                className="w-full h-12"
                                placeholder={`Enter ${field.label}`}
                                required
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}

                  <div className="pt-4">
                    <Button
                      type="submit"
                      disabled={loading || !isFormValid}
                      className={`w-full py-7 text-lg font-semibold shadow-lg transition-all duration-300 ${
                        isFormValid
                          ? "bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700"
                          : "bg-gray-400 cursor-not-allowed"
                      }`}
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
                          Analyzing Your Results...
                        </span>
                      ) : (
                        <span className="flex items-center justify-center gap-2">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                          </svg>
                          Get Kidney Health Assessment
                        </span>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Right column - Results & Tips */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="shadow-xl border-0 rounded-2xl h-full bg-white/90 backdrop-blur-sm">
              <CardContent className="p-8">
                <div className="flex items-center gap-3 mb-6">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="text-blue-600"
                  >
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                  <h2 className="text-2xl font-bold text-gray-800">
                    Assessment Results
                  </h2>
                </div>

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
                      className={`p-6 rounded-xl border ${
                        result.error
                          ? "bg-red-50 border-red-200"
                          : result.diagnosis?.toLowerCase().includes("ckd")
                          ? "bg-yellow-50 border-yellow-200"
                          : "bg-green-50 border-green-200"
                      }`}
                    >
                      {getDiagnosisMessage(result)}
                    </div>
                    {getExplanation(result)}
                    {getDisclaimer(result)}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-center">
                    <div className="w-28 h-28 mb-6 rounded-full bg-gray-100 flex items-center justify-center">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="48"
                        height="48"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="text-gray-400"
                      >
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                      </svg>
                    </div>
                    <h3 className="text-xl font-medium text-gray-700 mb-3">
                      No results yet
                    </h3>
                    <p className="text-gray-500 text-base max-w-xs">
                      Complete and submit the form to receive your personalized
                      kidney health assessment.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Health tips card */}
            <Card className="shadow-xl border-0 rounded-2xl bg-indigo-50 border-indigo-100">
              <CardContent className="p-8">
                <div className="flex items-center gap-3 mb-5">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="text-indigo-600"
                  >
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  </svg>
                  <h3 className="font-semibold text-xl text-indigo-800">
                    Kidney Health Tips
                  </h3>
                </div>
                <ul className="space-y-3 text-base text-indigo-700">
                  <li className="flex items-start gap-3">
                    <span className="text-indigo-500">•</span>
                    <span>
                      Stay hydrated by drinking plenty of water throughout the
                      day
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-indigo-500">•</span>
                    <span>
                      Maintain a balanced diet low in sodium and processed foods
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-indigo-500">•</span>
                    <span>
                      Monitor and control your blood pressure regularly
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-indigo-500">•</span>
                    <span>
                      Engage in regular physical activity to maintain a healthy
                      weight
                    </span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-indigo-500">•</span>
                    <span>
                      Limit the use of NSAIDs and consult your doctor about
                      medications
                    </span>
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
          animation: float1 12s ease-in-out infinite;
        }
        .animate-float2 {
          animation: float2 14s ease-in-out infinite;
        }
        .animate-float3 {
          animation: float3 16s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
