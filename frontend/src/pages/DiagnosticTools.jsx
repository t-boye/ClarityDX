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
import {
  FaStethoscope,
  FaHeart,
  FaVirus,
  FaFlask,
  FaArrowRight,
} from "react-icons/fa";
import { MdOutlineHealthAndSafety, MdBloodtype } from "react-icons/md";
import { GiLungs } from "react-icons/gi";
import { LuBrainCircuit } from "react-icons/lu"; // Import a suitable icon for SymScan

const DiagnosticTools = () => {
  const tools = [
    {
      title: "Malaria Diagnosis",
      description:
        "Utilize our AI-powered system for rapid malaria assessment.",
      icon: <FaVirus className="text-red-500" size={24} />,
      path: "/malaria-diagnosis",
    },
    {
      title: "Hepatitis C Diagnosis",
      description: "Screen for Hepatitis C with our advanced diagnostic tool.",
      icon: <FaFlask className="text-yellow-500" size={24} />,
      path: "/hepatitis-diagnosis",
    },
    {
      title: "Heart Disease Diagnosis",
      description:
        "Assess your cardiovascular health and identify potential risks.",
      icon: <FaHeart className="text-pink-500" size={24} />,
      path: "/heart-disease-diagnosis",
    },
    {
      title: "Kidney Disease Diagnosis",
      description: "Evaluate kidney function and health status effectively.",
      icon: <MdOutlineHealthAndSafety className="text-blue-500" size={24} />,
      path: "/kidney-disease-diagnosis",
    },
    {
      title: "SymScan Symptom Analysis", // Title for SymScan
      description:
        "Input your symptoms to receive an AI-driven potential diagnosis.", // Description for SymScan
      icon: <LuBrainCircuit className="text-purple-600" size={24} />, // Choose a suitable icon and color
      path: "/symscan",
    },
    // Uncomment these as needed.
    // {
    //   title: "Respiratory Diagnosis",
    //   description: "Evaluate symptoms related to lung conditions.",
    //   icon: <GiLungs className="text-green-500" size={24} />,
    //   path: "/respiratory-diagnosis",
    // },
    // {
    //   title: "Blood Disorder Diagnosis",
    //   description: "Assess potential blood-related conditions.",
    //   icon: <MdBloodtype className="text-red-600" size={24} />,
    //   path: "/blood-disorder-diagnosis",
    // },
  ];

  return (
    <div className="container mx-auto p-6 md:p-8 lg:p-10">
      <div className="text-center mb-12 space-y-4">
        <h2 className="text-4xl font-extrabold text-gray-900 leading-tight">
          Our Diagnostic Tools
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Empowering you with AI-powered health assessments. Select a tool below
          to begin your journey towards better health understanding.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        {tools.map((tool, index) => (
          <Card
            key={index}
            className="group flex flex-col justify-between shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 hover:border-indigo-500 border-2 border-gray-100 rounded-xl"
          >
            <CardHeader className="flex flex-row items-center space-x-4 pb-2">
              <div className="flex-shrink-0">{tool.icon}</div>
              <CardTitle className="text-xl font-bold text-gray-800">
                {tool.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-grow pt-0">
              <CardDescription className="text-base text-gray-700 mb-6">
                {tool.description}
              </CardDescription>
              <Button
                asChild
                className="w-full text-lg py-3 rounded-lg flex items-center justify-center space-x-2"
              >
                <Link to={tool.path}>
                  <span>Start Diagnosis</span>
                  <FaArrowRight className="ml-2 group-hover:translate-x-1 transition-transform duration-200" />
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
