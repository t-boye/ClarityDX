import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
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
      "AST/ALT": formData.ALT
        ? Number(formData.AST) / Number(formData.ALT)
        : null,
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

  // Group form fields into categories
  const formFieldGroups = [
    {
      title: "Patient Information",
      fields: [
        { name: "Age", label: "Age (years)", type: "number" },
        {
          name: "Sex",
          label: "Sex",
          type: "select",
          options: [
            { value: "m", label: "Male" },
            { value: "f", label: "Female" },
          ],
        },
        {
          name: "AgeGroup_Middle",
          label: "Middle Age Group (35-55)",
          type: "select",
          options: [
            { value: "0", label: "No" },
            { value: "1", label: "Yes" },
          ],
        },
        {
          name: "AgeGroup_Old",
          label: "Older Age Group (55+)",
          type: "select",
          options: [
            { value: "0", label: "No" },
            { value: "1", label: "Yes" },
          ],
        },
      ],
    },
    {
      title: "Liver Function Tests",
      fields: [
        { name: "ALB", label: "Albumin (g/dL)", type: "number" },
        { name: "ALP", label: "Alkaline Phosphatase (U/L)", type: "number" },
        { name: "ALT", label: "ALT (U/L)", type: "number" },
        { name: "AST", label: "AST (U/L)", type: "number" },
        { name: "BIL", label: "Bilirubin (mg/dL)", type: "number" },
        { name: "CHE", label: "Cholinesterase (U/L)", type: "number" },
        { name: "GGT", label: "GGT (U/L)", type: "number" },
        { name: "PROT", label: "Protein (g/dL)", type: "number" },
        { name: "AST/ALT", label: "AST/ALT Ratio", type: "number" },
      ],
    },
    {
      title: "Other Blood Tests",
      fields: [
        { name: "CHOL", label: "Cholesterol (mg/dL)", type: "number" },
        { name: "CREA", label: "Creatinine (mg/dL)", type: "number" },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 py-8 px-4">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden -z-10">
        <div className="absolute top-0 left-0 w-32 h-32 rounded-full bg-blue-200 opacity-20 animate-float1"></div>
        <div className="absolute top-1/4 right-0 w-48 h-48 rounded-full bg-green-200 opacity-20 animate-float2"></div>
        <div className="absolute bottom-0 left-1/3 w-40 h-40 rounded-full bg-blue-100 opacity-15 animate-float3"></div>
      </div>

      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            Hepatitis C Risk Assessment
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Enter your laboratory results to assess your risk for Hepatitis C
            infection
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
                                  handleChange({
                                    target: { name: field.name, value },
                                  })
                                }
                                value={formData[field.name].toString()}
                              >
                                <SelectTrigger
                                  id={field.name}
                                  className="w-full"
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
                                value={formData[field.name]}
                                onChange={handleChange}
                                className="w-full"
                                placeholder={`Enter ${field.label}`}
                              />
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
                      "Assess Hepatitis C Risk"
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
                          : result.diagnosis
                              ?.toLowerCase()
                              .includes("hepatitis c detected")
                          ? "bg-yellow-50 border-yellow-200"
                          : "bg-green-50 border-green-200"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        {result.error ? (
                          <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                        ) : result.diagnosis
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

                    {!result.error && result.probabilities && (
                      <div className="bg-white p-4 rounded-lg border shadow-sm">
                        <h4 className="font-medium mb-3">
                          Risk Probability Breakdown
                        </h4>
                        <div className="space-y-3">
                          {result.probabilities.map((prob, index) => (
                            <div
                              key={index}
                              className="flex items-center gap-3"
                            >
                              <span className="text-sm font-medium w-24">
                                {index === 0
                                  ? "Low Risk"
                                  : index === 1
                                  ? "Medium Risk"
                                  : "High Risk"}
                                :
                              </span>
                              <div className="flex-1 flex items-center gap-2">
                                <div className="w-full bg-gray-100 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${
                                      index === 0
                                        ? "bg-green-500"
                                        : index === 1
                                        ? "bg-yellow-500"
                                        : "bg-red-500"
                                    }`}
                                    style={{ width: `${prob * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-sm font-mono w-12">
                                  {(prob * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {!result.error && result.interpretation && (
                      <div className="bg-white p-4 rounded-lg border shadow-sm">
                        <h4 className="font-medium mb-3">Interpretation</h4>
                        <div className="space-y-3">
                          {Object.entries(result.interpretation).map(
                            ([key, value]) => (
                              <div key={key}>
                                {key === "significant_risk_factors" ? (
                                  <>
                                    <h5 className="font-semibold">
                                      Significant Risk Factors:
                                    </h5>
                                    <p className="text-sm">{value}</p>
                                  </>
                                ) : key === "disclaimer" ? (
                                  <p className="text-xs italic text-gray-500">
                                    {value}
                                  </p>
                                ) : (
                                  <>
                                    <h5 className="font-semibold">
                                      {key.replace(/_/g, " ")}:
                                    </h5>
                                    {Array.isArray(value) ? (
                                      value.map((item, i) => (
                                        <p key={i} className="text-sm">
                                          {item.reason}:{" "}
                                          {item.probability.toFixed(2)}
                                        </p>
                                      ))
                                    ) : (
                                      <p className="text-sm">{value}</p>
                                    )}
                                  </>
                                )}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="w-24 h-24 mb-4 rounded-full bg-gray-100 flex items-center justify-center">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="40"
                        height="40"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="text-gray-400"
                      >
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                        <path d="M12 8v4l3 3"></path>
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">
                      No results yet
                    </h3>
                    <p className="text-gray-500 text-sm max-w-xs">
                      Submit your lab results to receive a Hepatitis C risk
                      assessment.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Health tips card */}
            <Card className="shadow-lg border-0 rounded-xl bg-indigo-50 border-indigo-100">
              <CardContent className="p-6">
                <h3 className="font-semibold text-indigo-800 mb-3">
                  Hepatitis C Prevention Tips
                </h3>
                <ul className="space-y-2 text-sm text-indigo-700">
                  <li className="flex items-start gap-2">
                    <span>•</span> Avoid sharing needles or personal items that
                    may have blood on them
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Ensure safe medical procedures and proper
                    sterilization of equipment
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Practice safe sex using condoms
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Get tested if you're at risk or were born
                    between 1945-1965
                  </li>
                  <li className="flex items-start gap-2">
                    <span>•</span> Consider vaccination for Hepatitis A and B to
                    protect your liver
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
