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
import { AlertCircle, CheckCircle2, AlertTriangle } from "lucide-react";
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

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="shadow-lg p-6">
        <h2 className="text-xl font-bold text-center mb-4">
          Hepatitis C Diagnosis
        </h2>
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"
        >
          {/* Form inputs... */}
          <div>
            <Label>Age</Label>
            <Input
              type="number"
              name="Age"
              value={formData.Age}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>Sex</Label>
            <Select
              onValueChange={(value) =>
                setFormData({ ...formData, Sex: value })
              }
              value={formData.Sex}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select sex" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="m">Male</SelectItem>
                <SelectItem value="f">Female</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>ALB</Label>
            <Input
              type="number"
              name="ALB"
              value={formData.ALB}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>ALP</Label>
            <Input
              type="number"
              name="ALP"
              value={formData.ALP}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>ALT</Label>
            <Input
              type="number"
              name="ALT"
              value={formData.ALT}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>AST</Label>
            <Input
              type="number"
              name="AST"
              value={formData.AST}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>BIL</Label>
            <Input
              type="number"
              name="BIL"
              value={formData.BIL}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>CHE</Label>
            <Input
              type="number"
              name="CHE"
              value={formData.CHE}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>CHOL</Label>
            <Input
              type="number"
              name="CHOL"
              value={formData.CHOL}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>CREA</Label>
            <Input
              type="number"
              name="CREA"
              value={formData.CREA}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>GGT</Label>
            <Input
              type="number"
              name="GGT"
              value={formData.GGT}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>PROT</Label>
            <Input
              type="number"
              name="PROT"
              value={formData.PROT}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>AST/ALT</Label>
            <Input
              type="number"
              name="AST/ALT"
              value={formData["AST/ALT"]}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <Label>AgeGroup_Middle</Label>
            <Select
              onValueChange={(value) =>
                setFormData({ ...formData, AgeGroup_Middle: Number(value) })
              }
              value={String(formData.AgeGroup_Middle)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">No</SelectItem>
                <SelectItem value="1">Yes</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label>AgeGroup_Old</Label>
            <Select
              onValueChange={(value) =>
                setFormData({ ...formData, AgeGroup_Old: Number(value) })
              }
              value={String(formData.AgeGroup_Old)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">No</SelectItem>
                <SelectItem value="1">Yes</SelectItem>
              </SelectContent>
            </Select>
          </div>
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

        {error && (
          <Alert variant="destructive" className="mt-4">
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
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
