import React from "react";
import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FaStethoscope, FaHeart, FaVirus, FaFlask } from "react-icons/fa";
import { MdOutlineHealthAndSafety, MdBloodtype } from "react-icons/md";
import { GiLungs } from "react-icons/gi";

const DiagnosticTools = () => {
  const tools = [
    {
      title: "Malaria Diagnosis",
      description: "Use our expert system to assess the likelihood of malaria.",
      icon: <FaVirus className="text-red-500" size={20} />,
      path: "/malaria-diagnosis",
    },
    {
      title: "Hepatitis C Diagnosis",
      description: "Check for Hepatitis C using our diagnostic tool.",
      icon: <FaFlask className="text-yellow-500" size={20} />,
      path: "/hepatitis-diagnosis",
    },
    {
      title: "Heart Disease Diagnosis",
      description: "Evaluate your risk of heart disease.",
      icon: <FaHeart className="text-pink-500" size={20} />,
      path: "/heart-disease-diagnosis",
    },
    {
      title: "Kidney Disease Diagnosis",
      description: "Assess your kidney health with our diagnostic tool.",
      icon: <MdOutlineHealthAndSafety className="text-blue-500" size={20} />,
      path: "/kidney-disease-diagnosis",
    },
    // {
    //   title: "Respiratory Diagnosis",
    //   description: "Evaluate symptoms related to lung conditions.",
    //   icon: <GiLungs className="text-green-500" size={20} />,
    //   path: "/respiratory-diagnosis",
    // },
    // {
    //   title: "Blood Disorder Diagnosis",
    //   description: "Assess potential blood-related conditions.",
    //   icon: <MdBloodtype className="text-red-600" size={20} />,
    //   path: "/blood-disorder-diagnosis",
    // },
  ];

  return (
    <div className="container mx-auto p-6">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold mb-2">Diagnostic Tools</h2>
        <p className="text-muted-foreground">
          Select a diagnostic tool to begin your health assessment
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tools.map((tool, index) => (
          <Card
            key={index}
            className="shadow-md hover:shadow-lg transition-shadow duration-300 hover:border-primary"
          >
            <CardHeader>
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                {tool.icon}
                {tool.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="mb-4">
                {tool.description}
              </CardDescription>
              <Button asChild className="w-full">
                <Link to={tool.path}>
                  <FaStethoscope className="mr-2" />
                  Start Diagnosis
                </Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default DiagnosticTools;
