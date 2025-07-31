import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Select, {
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import axios from "axios";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  AlertCircle,
  CheckCircle2,
  AlertTriangle,
  FlaskConical,
} from "lucide-react";
import { BASE_API_URL } from "../utils/apiConfig";

export default function HepatitisCDiagnosis() {
  const [formData, setFormData] = useState({
    Age: "",
    Sex: "m",
    ALB: "",
    ALP: "",
    ALT: "",
    AST: "",
    BIL: "",
    CHE: "",
    CHOL: "",
    CREA: "",
    GGT: "",
    PROT: "",
    "AST/ALT": "",
    AgeGroup_Middle: 0,
    AgeGroup_Old: 0,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    let newValue = value;

    if (
      [
        "Age",
        "ALB",
        "ALP",
        "ALT",
        "AST",
        "BIL",
        "CHE",
        "CHOL",
        "CREA",
        "GGT",
        "PROT",
        "AST/ALT",
      ].includes(name)
    ) {
      newValue = Number(value);
    }
    setFormData({ ...formData, [name]: newValue });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    let astAltRatio = null;
    if (formData.ALT !== "" && Number(formData.ALT) !== 0) {
      astAltRatio = Number(formData.AST) / Number(formData.ALT);
    }

    const backendFormData = {
      Age: formData.Age ? Number(formData.Age) : null,
      Sex: formData.Sex,
      ALB: formData.ALB ? Number(formData.ALB) : null,
      ALP: formData.ALP ? Number(formData.ALP) : null,
      ALT: formData.ALT ? Number(formData.ALT) : null,
      AST: formData.AST ? Number(formData.AST) : null,
      BIL: formData.BIL ? Number(formData.BIL) : null,
      CHE: formData.CHE ? Number(formData.CHE) : null,
      CHOL: formData.CHOL ? Number(formData.CHOL) : null,
      CREA: formData.CREA ? Number(formData.CREA) : null,
      GGT: formData.GGT ? Number(formData.GGT) : null,
      PROT: formData.PROT ? Number(formData.PROT) : null,
      "AST/ALT": astAltRatio,
      AgeGroup_Middle: formData.AgeGroup_Middle,
      AgeGroup_Old: formData.AgeGroup_Old,
    };

    try {
      const response = await axios.post(
        `${BASE_API_URL}/predict/hepatitis_c`,
        backendFormData
      );
      setResult(response.data);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || "An error occurred.");
        console.error("Axios error:", err.response?.data || err.message);
      } else {
        setError("Failed to connect to the server.");
        console.error("Non-Axios error:", err);
      }
    } finally {
      setLoading(false);
    }
  };

  // Group related fields together
  const fieldGroups = [
    {
      title: "Patient Information",
      icon: "👤",
      fields: [
        { name: "Age", label: "Age", type: "number", unit: "years" },
        {
          name: "Sex",
          label: "Sex",
          type: "select",
          options: [
            { value: "m", label: "Male" },
            { value: "f", label: "Female" },
          ],
        },
      ],
    },
    {
      title: "Liver Function Tests",
      icon: "🧪",
      fields: [
        { name: "ALB", label: "Albumin", type: "number", unit: "g/dL" },
        {
          name: "ALP",
          label: "Alkaline Phosphatase",
          type: "number",
          unit: "U/L",
        },
        {
          name: "ALT",
          label: "Alanine Transaminase",
          type: "number",
          unit: "U/L",
        },
        {
          name: "AST",
          label: "Aspartate Transaminase",
          type: "number",
          unit: "U/L",
        },
        { name: "BIL", label: "Bilirubin", type: "number", unit: "mg/dL" },
        { name: "CHE", label: "Cholinesterase", type: "number", unit: "kU/L" },
      ],
    },
    {
      title: "Other Blood Tests",
      icon: "💉",
      fields: [
        { name: "CHOL", label: "Cholesterol", type: "number", unit: "mg/dL" },
        { name: "CREA", label: "Creatinine", type: "number", unit: "mg/dL" },
        {
          name: "GGT",
          label: "Gamma-Glutamyl Transferase",
          type: "number",
          unit: "U/L",
        },
        { name: "PROT", label: "Protein", type: "number", unit: "g/dL" },
        { name: "AST/ALT", label: "AST/ALT Ratio", type: "number" },
      ],
    },
    {
      title: "Age Groups",
      icon: "📊",
      fields: [
        {
          name: "AgeGroup_Middle",
          label: "Middle Age Group",
          type: "select",
          options: [
            { value: "0", label: "No (Under 35)" },
            { value: "1", label: "Yes (35-55)" },
          ],
        },
        {
          name: "AgeGroup_Old",
          label: "Old Age Group",
          type: "select",
          options: [
            { value: "0", label: "No (Under 55)" },
            { value: "1", label: "Yes (55+)" },
          ],
        },
      ],
    },
  ];

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6">
      <Card className="shadow-lg overflow-hidden border border-gray-200">
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-4 text-white">
          <div className="flex items-center gap-3">
            <FlaskConical className="h-6 w-6" />
            <h2 className="text-xl md:text-2xl font-bold">
              Hepatitis C Diagnosis Tool
            </h2>
          </div>
          <p className="text-sm text-blue-100 mt-1">
            Enter patient blood test results to assess Hepatitis C risk
          </p>
        </div>

        <div className="p-4 md:p-6 bg-gray-50">
          <form onSubmit={handleSubmit} className="space-y-6">
            {fieldGroups.map((group, groupIndex) => (
              <div key={groupIndex} className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{group.icon}</span>
                  <h3 className="font-semibold text-gray-800 text-lg border-b-2 border-blue-200 pb-1">
                    {group.title}
                  </h3>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {group.fields.map((field) => (
                    <div
                      key={field.name}
                      className="space-y-1 bg-white p-3 rounded-lg shadow-sm border border-gray-100"
                    >
                      <div className="flex items-center justify-between">
                        <Label
                          htmlFor={field.name}
                          className="text-sm font-medium text-gray-700 flex items-center gap-1"
                        >
                          <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-md">
                            {field.label}
                          </span>
                        </Label>
                        {field.unit && (
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                            {field.unit}
                          </span>
                        )}
                      </div>
                      {field.type === "select" ? (
                        <Select
                          onValueChange={(value) =>
                            setFormData({ ...formData, [field.name]: value })
                          }
                          value={formData[field.name]}
                        >
                          <SelectTrigger className="text-sm h-9 mt-1 border-gray-300">
                            <SelectValue
                              placeholder={`Select ${field.label}`}
                            />
                          </SelectTrigger>
                          <SelectContent>
                            {field.options.map((option) => (
                              <SelectItem
                                key={option.value}
                                value={option.value}
                                className="text-sm"
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
                          type="number"
                          step="any"
                          value={formData[field.name]}
                          onChange={handleChange}
                          className="text-sm h-9 mt-1"
                          required
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}

            <div className="pt-2">
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white py-2 shadow-md"
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
                    <FlaskConical className="h-4 w-4" />
                    Run Diagnosis
                  </span>
                )}
              </Button>
            </div>
          </form>

          {error && (
            <Alert variant="destructive" className="mt-6">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {result && (
            <div className="mt-6 space-y-4">
              <div
                className={`p-4 rounded-lg border ${
                  result.error ||
                  (typeof result === "object" &&
                    result.diagnosis
                      ?.toLowerCase()
                      .includes("hepatitis c detected"))
                    ? "bg-red-50 border-red-200"
                    : "bg-green-50 border-green-200"
                }`}
              >
                <div className="flex items-start gap-3">
                  {result.error ? (
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                  ) : typeof result === "object" &&
                    result.diagnosis
                      ?.toLowerCase()
                      .includes("hepatitis c detected") ? (
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                  ) : (
                    <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  )}
                  <div>
                    <h3 className="font-semibold text-lg">
                      {result.error ? "Error" : "Diagnosis Result"}
                    </h3>
                    <p className="text-sm">
                      {result.error ? result.error : result.diagnosis}
                    </p>
                    {result.probability && (
                      <p className="text-sm mt-2">
                        <span className="font-medium">Confidence:</span>{" "}
                        <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                          {(result.probability * 100).toFixed(1)}%
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-800 mb-2 flex items-center gap-2">
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
                  Interpretation Guidance
                </h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500">•</span>
                    AST/ALT ratio {">"} 1 suggests possible liver fibrosis
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500">•</span>
                    Elevated ALT levels may indicate liver inflammation
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500">•</span>
                    Low albumin can suggest impaired liver function
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500">•</span>
                    High bilirubin may indicate liver or bile duct issues
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
