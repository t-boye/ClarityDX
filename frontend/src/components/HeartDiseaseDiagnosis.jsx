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

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

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
        "http://127.0.0.1:8000/api/predict/heart_disease",
        apiData,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (response.status !== 200) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      setResult(response.data);
    } catch (err) {
      console.error("Error diagnosing Heart Disease", err);
      setError(err.message || "Failed to get diagnosis. Please try again.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

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
      result.diagnosis.toLowerCase().includes("possible indication")
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

  const getRiskFactorMessage = (result) => {
    if (
      result.interpretation &&
      result.interpretation.significant_risk_factors
    ) {
      return (
        <div className="bg-white p-4 rounded-lg border shadow-sm mt-4">
          <h4 className="font-medium mb-3">Risk Factor Analysis</h4>
          <p className="text-sm">
            {result.interpretation.significant_risk_factors.message}
          </p>
          {result.interpretation.significant_risk_factors.factors && (
            <ul className="list-disc list-inside ml-5">
              {Object.entries(
                result.interpretation.significant_risk_factors.factors
              ).map(([factor, value]) => (
                <li key={factor} className="text-sm">
                  {factor}: {value}
                </li>
              ))}
            </ul>
          )}
        </div>
      );
    }
    return null;
  };

  const getDisclaimer = (result) => {
    if (result.interpretation && result.interpretation.disclaimer) {
      return (
        <p className="text-xs italic text-gray-500 mt-4">
          {result.interpretation.disclaimer}
        </p>
      );
    }
    return null;
  };

  return (
    <div className="max-w-5xl mx-auto p-6 min-h-screen flex flex-col justify-center">
      <Card className="shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4 text-center">
          Heart Disease Diagnosis
        </h2>

        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6"
        >
          <div>
            <Label htmlFor="age">Age</Label>
            <Input
              type="number"
              id="age"
              name="age"
              value={formData.age}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <Label htmlFor="sex">Sex</Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "sex", value } })
              }
              value={formData.sex}
            >
              <SelectTrigger id="sex" className="w-full">
                {formData.sex}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Male">Male</SelectItem>
                <SelectItem value="Female">Female</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="cp">Chest Pain Type</Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "cp", value } })
              }
            >
              <SelectTrigger id="cp" className="w-full">
                {formData.cp}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Typical Angina">Typical Angina</SelectItem>
                <SelectItem value="Atypical Angina">Atypical Angina</SelectItem>
                <SelectItem value="Non-anginal Pain">
                  Non-anginal Pain
                </SelectItem>
                <SelectItem value="Asymptomatic">Asymptomatic</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="trestbps">Resting Blood Pressure</Label>
            <Input
              type="number"
              id="trestbps"
              name="trestbps"
              value={formData.trestbps}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <Label htmlFor="chol">Cholesterol</Label>
            <Input
              type="number"
              id="chol"
              name="chol"
              value={formData.chol}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <Label htmlFor="fbs">Fasting Blood Sugar &gt; 120 mg/dl</Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "fbs", value } })
              }
            >
              <SelectTrigger id="fbs" className="w-full">
                {formData.fbs}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="No">No</SelectItem>
                <SelectItem value="Yes">Yes</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="restecg">Resting ECG</Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "restecg", value } })
              }
            >
              <SelectTrigger id="restecg" className="w-full">
                {formData.restecg}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Normal">Normal</SelectItem>
                <SelectItem value="ST-T Wave Abnormality">
                  ST-T Wave Abnormality
                </SelectItem>
                <SelectItem value="Left Ventricular Hypertrophy">
                  Left Ventricular Hypertrophy
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="thalach">Max Heart Rate Achieved</Label>
            <Input
              type="number"
              id="thalach"
              name="thalach"
              value={formData.thalach}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <Label htmlFor="exang">Exercise Induced Angina</Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "exang", value } })
              }
            >
              <SelectTrigger id="exang" className="w-full">
                {formData.exang}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="No">No</SelectItem>
                <SelectItem value="Yes">Yes</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="oldpeak">ST Depression Induced by Exercise</Label>
            <Input
              type="number"
              step="0.1"
              id="oldpeak"
              name="oldpeak"
              value={formData.oldpeak}
              onChange={handleChange}
              required
            />
          </div>

          <div>
            <Label htmlFor="slope">Slope of Peak Exercise ST Segment</Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "slope", value } })
              }
            >
              <SelectTrigger id="slope" className="w-full">
                {formData.slope}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Upsloping">Upsloping</SelectItem>
                <SelectItem value="Flat">Flat</SelectItem>
                <SelectItem value="Downsloping">Downsloping</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="ca">
              Number of Major Vessels Colored by Fluoroscopy
            </Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "ca", value } })
              }
            >
              <SelectTrigger id="ca" className="w-full">
                {formData.ca}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">0</SelectItem>
                <SelectItem value="1">1</SelectItem>
                <SelectItem value="2">2</SelectItem>
                <SelectItem value="3">3</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="thal">Thalassemia</Label>
            <Select
              onValueChange={(value) =>
                handleChange({ target: { name: "thal", value } })
              }
            >
              <SelectTrigger id="thal" className="w-full">
                {formData.thal}
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Normal">Normal</SelectItem>
                <SelectItem value="Fixed Defect">Fixed Defect</SelectItem>
                <SelectItem value="Reversible Defect">
                  Reversible Defect
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Full-width button */}
          <div className="col-span-1 sm:col-span-2 md:col-span-3 flex justify-center">
            <Button
              type="submit"
              disabled={loading}
              className="bg-blue-500 text-white w-full"
            >
              {loading ? "Diagnosing..." : "Diagnose"}
            </Button>
          </div>
        </form>

        {/* Diagnosis Result */}
        {loading && <p>Loading...</p>}

        {error && (
          <CardContent className="mt-4 p-4 bg-red-100 rounded">
            <p className="text-red-500">Error: {error}</p>
          </CardContent>
        )}

        {result && !error && (
          <CardContent className="mt-4 p-4 bg-green-100 rounded">
            {getDiagnosisMessage(result)}
            {getRiskFactorMessage(result)}
            {getDisclaimer(result)}
          </CardContent>
        )}
      </Card>
    </div>
  );
}
