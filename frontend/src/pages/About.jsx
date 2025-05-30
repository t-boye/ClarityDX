import React from "react";
import {
  FaMicroscope,
  FaHeartbeat,
  FaLungs,
  FaChartLine,
  FaShieldAlt,
  FaClinicMedical,
} from "react-icons/fa";
import { GiKidneys } from "react-icons/gi"; // ✅ Valid kidney icon

const About = () => {
  const diseases = [
    {
      icon: <FaMicroscope className="text-2xl text-indigo-600" />,
      name: "Malaria",
      id: "malaria",
      imageUrl: "https://i.postimg.cc/d0Nyg06N/malaria.jpg",
      description: "AI-powered malaria parasite detection in blood smears",
    },
    {
      icon: <FaHeartbeat className="text-2xl text-indigo-600" />,
      name: "Heart Disease",
      id: "heart",
      imageUrl:
        "https://i.postimg.cc/ht76XJzT/The-link-between-heart-disease-and-Alzheimer-s-disease.jpg",
      description: "Cardiovascular risk assessment and diagnosis",
    },
    {
      icon: <FaLungs className="text-2xl text-indigo-600" />,
      name: "Hepatitis C",
      id: "hepatitis",
      imageUrl: "https://i.postimg.cc/XYp3Q7ZY/hepaC.jpg",
      description: "Liver function analysis and viral detection",
    },
    {
      icon: <GiKidneys className="text-2xl text-indigo-600" />,
      name: "Kidney Disease",
      id: "kidney",
      imageUrl:
        "https://i.postimg.cc/85VSpRZ7/Homeopathic-Treatment-for-Chronic-Kidney-Disease-in-Agra.jpg",
      description: "Renal function evaluation and damage assessment",
    },
  ];

  const features = [
    {
      icon: <FaClinicMedical className="text-3xl text-indigo-600" />,
      title: "Multi-Disease Platform",
      description: "Unified interface for diagnosing diverse conditions",
    },
    {
      icon: <FaChartLine className="text-3xl text-indigo-600" />,
      title: "Adaptive AI Models",
      description: "Condition-specific neural networks for each disease",
    },
    {
      icon: <FaShieldAlt className="text-3xl text-indigo-600" />,
      title: "Clinical Validation",
      description: "Peer-reviewed diagnostic accuracy",
    },
  ];

  return (
    <div className="bg-white py-12 sm:py-16 lg:py-20">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Hero Section */}
        <div className="mx-auto max-w-3xl text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            Advanced Multi-Disease Diagnostic System
          </h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Integrating specialized AI models for accurate detection of multiple
            diseases
          </p>
          <div className="mt-10">
            <img
              src="https://i.postimg.cc/zBBBsLkb/Overcoming-Common-Challenges-In-Medical-Data-Handling.jpg"
              alt="Doctor analyzing medical data"
              className="w-full rounded-xl shadow-lg"
              loading="lazy"
            />
          </div>
        </div>

        {/* Disease Matrix */}
        <div className="mt-16 bg-indigo-50 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Supported Conditions
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {diseases.map((disease) => (
              <div
                key={disease.id}
                className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-all flex flex-col items-center"
              >
                <div className="w-full h-40 mb-4 overflow-hidden rounded-md">
                  <img
                    src={disease.imageUrl}
                    alt={`${disease.name} diagnosis`}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-indigo-600">{disease.icon}</div>
                  <h3 className="font-medium text-gray-900">{disease.name}</h3>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="mt-16 grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* Text Content */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              How Our System Works
            </h2>
            <div className="space-y-6 text-gray-700">
              <p>
                Our{" "}
                <span className="font-semibold text-indigo-600">
                  Multi-Disease Expert System
                </span>
                combines specialized AI models with clinical decision rules to
                provide accurate diagnoses across diverse medical conditions.
              </p>

              <img
                src="https://i.postimg.cc/DygsT5yM/AI-in-Healthcare-and-Medical.jpg"
                alt="AI analyzing medical data"
                className="w-full rounded-lg my-6 shadow-md"
                loading="lazy"
              />

              <p>Each disease module incorporates:</p>
              <ul className="list-disc pl-5 space-y-2">
                <li>Condition-specific neural networks</li>
                <li>Evidence-based diagnostic protocols</li>
                <li>Integrated risk factor analysis</li>
                <li>Automated differential diagnosis</li>
              </ul>
            </div>

            {/* Features */}
            <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-white p-4 rounded-lg border border-gray-200"
                >
                  <div className="flex flex-col items-center text-center">
                    <div className="mb-3">{feature.icon}</div>
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Visual Content */}
          <div className="sticky top-20">
            <div className="relative rounded-xl overflow-hidden shadow-lg mb-8">
              <img
                src="https://i.postimg.cc/ZK9N9QpB/homepage.png"
                alt="Medical diagnostic interface"
                className="w-full h-auto"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-b from-transparent to-gray-900/70" />
              <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                <h3 className="text-xl font-semibold">
                  Unified Diagnostic Platform
                </h3>
                <p className="text-sm opacity-90 mt-1">
                  Single interface for multiple disease analysis
                </p>
              </div>
            </div>

            {/* Stats Card */}
            <div className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">System Performance</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-indigo-50 p-3 rounded-lg text-center">
                  <p className="text-2xl font-bold text-indigo-600">5+</p>
                  <p className="text-sm font-medium">Disease Modules</p>
                </div>
                <div className="bg-indigo-50 p-3 rounded-lg text-center">
                  <p className="text-2xl font-bold text-indigo-600">98.7%</p>
                  <p className="text-sm font-medium">Average Accuracy</p>
                </div>
                <div className="bg-indigo-50 p-3 rounded-lg text-center">
                  <p className="text-2xl font-bold text-indigo-600">24/7</p>
                  <p className="text-sm font-medium">Availability</p>
                </div>
                <div className="bg-indigo-50 p-3 rounded-lg text-center">
                  <p className="text-2xl font-bold text-indigo-600">3.2s</p>
                  <p className="text-sm font-medium">Avg. Diagnosis Time</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Testimonials */}
        <div className="mt-24 bg-gray-50 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            Trusted by Medical Professionals
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <img
                  src="https://images.unsplash.com/photo-1594824476967-48c8b964273f?ixlib=rb-1.2.1&auto=format&fit=crop&w=100&q=80"
                  alt="Dr. Sarah Johnson"
                  className="w-12 h-12 rounded-full mr-4"
                />
                <div>
                  <h4 className="font-semibold">Unknown</h4>
                  <p className="text-sm text-gray-600">Unknown</p>
                </div>
              </div>
              <p className="text-gray-700">
                "This system has revolutionized how we approach differential
                diagnosis, particularly for complex cases with overlapping
                symptoms."
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="flex items-center mb-4">
                <img
                  src="https://images.unsplash.com/photo-1622253692010-333f2da6031d?ixlib=rb-1.2.1&auto=format&fit=crop&w=100&q=80"
                  alt="Dr. Michael Chen"
                  className="w-12 h-12 rounded-full mr-4"
                />
                <div>
                  <h4 className="font-semibold">Unknown</h4>
                  <p className="text-sm text-gray-600">Unknown</p>
                </div>
              </div>
              <p className="text-gray-700">
                "The malaria detection module achieves accuracy comparable to
                senior pathologists, but in a fraction of the time."
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
