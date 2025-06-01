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
import { AlertCircle, CheckCircle2, AlertTriangle } from "lucide-react";
import { BASE_API_URL } from "../utils/apiConfig"; // <--- ADD THIS LINE!

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

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const apiData = {
        "Age (yrs)": formData["Age (yrs)"]
          ? parseFloat(formData["Age (yrs)"])
          : null,
        "Blood Pressure (mm/Hg)": formData["Blood Pressure (mm/Hg)"]
          ? parseFloat(formData["Blood Pressure (mm/Hg)"])
          : null,
        "Specific Gravity": formData["Specific Gravity"]
          ? parseFloat(formData["Specific Gravity"])
          : null,
        Albumin: formData.Albumin ? parseFloat(formData.Albumin) : null,
        Sugar: formData.Sugar ? parseFloat(formData.Sugar) : null,
        "Blood Glucose Random (mgs/dL)": formData[
          "Blood Glucose Random (mgs/dL)"
        ]
          ? parseFloat(formData["Blood Glucose Random (mgs/dL)"])
          : null,
        "Blood Urea (mgs/dL)": formData["Blood Urea (mgs/dL)"]
          ? parseFloat(formData["Blood Urea (mgs/dL)"])
          : null,
        "Serum Creatinine (mgs/dL)": formData["Serum Creatinine (mgs/dL)"]
          ? parseFloat(formData["Serum Creatinine (mgs/dL)"])
          : null,
        "Sodium (mEq/L)": formData["Sodium (mEq/L)"]
          ? parseFloat(formData["Sodium (mEq/L)"])
          : null,
        "Potassium (mEq/L)": formData["Potassium (mEq/L)"]
          ? parseFloat(formData["Potassium (mEq/L)"])
          : null,
        "Hemoglobin (gms)": formData["Hemoglobin (gms)"]
          ? parseFloat(formData["Hemoglobin (gms)"])
          : null,
        "Packed Cell Volume": formData["Packed Cell Volume"]
          ? parseFloat(formData["Packed Cell Volume"])
          : null,
        "White Blood Cells (cells/cmm)": formData[
          "White Blood Cells (cells/cmm)"
        ]
          ? parseFloat(formData["White Blood Cells (cells/cmm)"])
          : null,
        "Red Blood Cells (millions/cmm)": formData[
          "Red Blood Cells (millions/cmm)"
        ]
          ? parseFloat(formData["Red Blood Cells (millions/cmm)"])
          : null,
        "Red Blood Cells: normal":
          formData["Red Blood Cells: normal"] === "normal" ? 1 : 0,
        "Pus Cells: normal": formData["Pus Cells: normal"] === "normal" ? 1 : 0,
        "Pus Cell Clumps: present":
          formData["Pus Cell Clumps: present"] === "present" ? 1 : 0,
        "Bacteria: present":
          formData["Bacteria: present"] === "present" ? 1 : 0,
        "Hypertension: yes": formData["Hypertension: yes"] === "yes" ? 1 : 0,
        "Diabetes Mellitus: yes":
          formData["Diabetes Mellitus: yes"] === "yes" ? 1 : 0,
        "Coronary Artery Disease: yes":
          formData["Coronary Artery Disease: yes"] === "yes" ? 1 : 0,
        "Appetite: poor": formData["Appetite: poor"] === "poor" ? 1 : 0,
        "Pedal Edema: yes": formData["Pedal Edema: yes"] === "yes" ? 1 : 0,
        "Anemia: yes": formData["Anemia: yes"] === "yes" ? 1 : 0,
      };

      // THIS IS THE CRUCIAL CHANGE:
      const response = await axios.post(
        `${BASE_API_URL}/predict/ckd`, // <--- UPDATED URL HERE!
        apiData,
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      // Changed from !response.ok because axios throws an error for non-2xx status codes
      // and response.ok is not a property of axios responses.
      setResult(response.data);
      if (onDiagnosis) {
        onDiagnosis(response.data);
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // Handle Axios specific errors (e.g., network error, 4xx/5xx responses)
        setError(error.response?.data?.error || "An error occurred.");
        console.error("Axios error:", error.response?.data || error.message);
      } else {
        // Handle other types of errors
        setError("Failed to connect to the server.");
        console.error("Non-Axios error:", error);
      }
    } finally {
      setLoading(false);
    }
  };

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
      result.diagnosis &&
      result.diagnosis.toLowerCase().includes("high likelihood")
    ) {
      icon = (
        <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
      );
    }

    return (
      <>
        {icon}
        <div>
          <h3 className="font-semibold text-lg">Diagnosis Result</h3>
          <p className="text-sm">{result.diagnosis}</p>
        </div>
      </>
    );
  };

  const getExplanation = (result) => {
    if (result.explanation) {
      return (
        <div className="bg-white p-4 rounded-lg border shadow-sm mt-4">
          <h4 className="font-medium mb-3">Explanation</h4>
          <div className="space-y-3">
            {Object.entries(result.explanation).map(([key, value]) => (
              <div key={key}>
                <h5 className="font-semibold">{key.replace(/_/g, " ")}:</h5>
                {typeof value === "string" ? (
                  <p className="text-sm">{value}</p>
                ) : (
                  Object.entries(value).map(([reason, detail], index) => (
                    <p key={index} className="text-sm">
                      {reason}: {detail.toFixed(2)}
                    </p>
                  ))
                )}
              </div>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  const getDisclaimer = (result) => {
    if (result.explanation && result.explanation.disclaimer) {
      return (
        <p className="text-xs italic text-gray-500 mt-4">
          {result.explanation.disclaimer}
        </p>
      );
    }
    return null;
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="shadow-lg">
        <CardContent>
          <h2 className="text-2xl font-bold text-center mb-6">
            Kidney Disease Diagnosis
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            {Object.keys(formData).map((field) => (
              <div key={field} className="flex items-center space-x-3">
                <Label htmlFor={field} className="w-1/3 text-right">
                  {field}
                </Label>
                {selectOptions[field] ? (
                  <Select
                    onValueChange={(value) =>
                      handleChange({ target: { name: field, value } })
                    }
                    defaultValue={formData[field]}
                  >
                    <SelectTrigger id={field} className="w-2/3">
                      <SelectValue
                        placeholder={`Select ${field.replace(
                          /: yes|: normal|: present/g,
                          ""
                        )}`}
                      />
                    </SelectTrigger>
                    <SelectContent>
                      {selectOptions[field].map((option) => (
                        <SelectItem key={option} value={option}>
                          {option}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    id={field}
                    name={field}
                    type="number"
                    value={formData[field]}
                    onChange={handleChange}
                    className="w-2/3"
                  />
                )}
              </div>
            ))}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Diagnosing..." : "Diagnose"}
            </Button>
          </form>
          {result && (
            <div className="mt-6 space-y-4">
              <div className="p-4 rounded-lg border bg-green-50 border-green-200">
                {getDiagnosisMessage(result)}
              </div>
              {getExplanation(result)}
              {getDisclaimer(result)}
            </div>
          )}
          {error && (
            <Alert className="mt-4 text-red-600">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
