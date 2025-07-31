import React from "react";
import {
  FaMicroscope,
  FaHeartbeat,
  FaChartLine,
  FaShieldAlt,
  FaClinicMedical,
  FaUserMd,
  FaBrain,
  FaStethoscope,
} from "react-icons/fa";
import { GiKidneys } from "react-icons/gi";
import { MdHealthAndSafety } from "react-icons/md";

const About = () => {
  const diseases = [
    {
      icon: <FaMicroscope className="text-3xl text-blue-600" />,
      name: "Malaria",
      id: "malaria",
      imageUrl: "https://i.postimg.cc/d0Nyg06N/malaria.jpg",
      description: "AI-powered malaria parasite detection in blood smears.",
      color: "bg-blue-100",
    },
    {
      icon: <FaHeartbeat className="text-3xl text-red-600" />,
      name: "Heart Disease",
      id: "heart",
      imageUrl:
        "https://i.postimg.cc/ht76XJzT/The-link-between-heart-disease-and-Alzheimer-s-disease.jpg",
      description: "Cardiovascular health risk assessment and early diagnosis.",
      color: "bg-red-100",
    },
    {
      icon: <FaBrain className="text-3xl text-purple-600" />,
      name: "Hepatitis C",
      id: "hepatitis",
      imageUrl: "https://i.postimg.cc/XYp3Q7ZY/hepaC.jpg",
      description: "Liver function analysis and Hepatitis C viral detection.",
      color: "bg-purple-100",
    },
    {
      icon: <GiKidneys className="text-3xl text-green-600" />,
      name: "Kidney Disease",
      id: "kidney",
      imageUrl:
        "https://i.postimg.cc/85VSpRZ7/Homeopathic-Treatment-for-Chronic-Kidney-Disease-in-Agra.jpg",
      description:
        "Comprehensive renal health evaluation and damage assessment.",
      color: "bg-green-100",
    },
    {
      icon: <FaStethoscope className="text-3xl text-indigo-600" />,
      name: "Symptom Scan",
      id: "symscan",
      imageUrl: "https://i.postimg.cc/tTx1n7qC/download-1.jpg",
      description:
        "General symptom checker for preliminary disease predictions.",
      color: "bg-indigo-100",
    },
  ];

  const features = [
    {
      icon: <FaClinicMedical className="text-4xl text-blue-600" />,
      title: "Multi-Disease Platform",
      description: "Unified interface for diagnosing diverse conditions",
    },
    {
      icon: <FaChartLine className="text-4xl text-blue-600" />,
      title: "Adaptive AI Models",
      description: "Condition-specific neural networks for each disease",
    },
    {
      icon: <FaShieldAlt className="text-4xl text-blue-600" />,
      title: "Clinical Validation",
      description: "Peer-reviewed diagnostic accuracy",
    },
  ];

  const stats = [
    { value: "4+", label: "Disease Modules" },
    { value: "98.7%", label: "Average Accuracy" },
    { value: "24/7", label: "Availability" },
    { value: "3.2s", label: "Avg. Diagnosis Time" },
  ];

  return (
    <div className="bg-white py-12 sm:py-16 lg:py-20">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Hero Section */}
        <div className="mx-auto max-w-4xl text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-6">
            <MdHealthAndSafety className="text-blue-500 text-5xl" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
              About ClarityDX
            </h1>
          </div>
          <p className="mt-6 text-xl leading-8 text-gray-600">
            AI-powered diagnostic platform delivering precise, rapid medical
            assessments with clinical-grade accuracy
          </p>
          <div className="mt-10 rounded-xl overflow-hidden shadow-xl">
            <img
              src="https://i.postimg.cc/DygsT5yM/AI-in-Healthcare-and-Medical.jpg"
              alt="AI analyzing medical data"
              className="w-full h-auto object-cover"
              loading="lazy"
            />
          </div>
        </div>

        {/* Disease Matrix */}
        <div className="mt-16 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-8 shadow-sm">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-10">
            Our Diagnostic Capabilities
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {diseases.map((disease) => (
              <div
                key={disease.id}
                className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all flex flex-col items-center text-center"
              >
                <div className={`${disease.color} p-4 rounded-full mb-4`}>
                  {disease.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {disease.name}
                </h3>
                <div className="w-full h-48 mb-4 overflow-hidden rounded-lg">
                  <img
                    src={disease.imageUrl}
                    alt={`${disease.name} diagnosis`}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                </div>
                <p className="text-gray-600">{disease.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="mt-20 grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* Text Content */}
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              How ClarityDX Works
            </h2>
            <div className="space-y-6 text-gray-700 text-lg">
              <p>
                Our{" "}
                <span className="font-semibold text-blue-600">
                  ClarityDX platform
                </span>
                combines specialized AI models with clinical decision rules to
                provide accurate diagnoses across diverse medical conditions.
              </p>

              <div className="mt-8 rounded-lg overflow-hidden shadow-lg">
                <img
                  src="https://i.postimg.cc/ZK9N9QpB/homepage.png"
                  alt="ClarityDX interface"
                  className="w-full h-auto"
                  loading="lazy"
                />
              </div>

              <p>Each diagnostic module incorporates:</p>
              <ul className="list-disc pl-6 space-y-3">
                <li>Condition-specific deep learning models</li>
                <li>Evidence-based diagnostic protocols</li>
                <li>Integrated risk factor analysis</li>
                <li>Automated differential diagnosis</li>
                <li>Real-time clinical decision support</li>
              </ul>
            </div>

            {/* Features */}
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-white p-6 rounded-xl border border-gray-200 hover:border-blue-300 transition-all shadow-sm"
                >
                  <div className="flex flex-col items-center text-center">
                    <div className="mb-4">{feature.icon}</div>
                    <h3 className="text-xl font-semibold mb-2 text-gray-900">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Visual Content */}
          <div className="sticky top-20 space-y-8">
            {/* Stats Card */}
            <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
              <h3 className="text-2xl font-semibold mb-6 text-center">
                System Performance
              </h3>
              <div className="grid grid-cols-2 gap-6">
                {stats.map((stat, index) => (
                  <div
                    key={index}
                    className="bg-blue-50 p-4 rounded-xl text-center hover:bg-blue-100 transition-colors"
                  >
                    <p className="text-3xl font-bold text-blue-600">
                      {stat.value}
                    </p>
                    <p className="text-sm font-medium text-gray-700">
                      {stat.label}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Testimonial */}
            <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200">
              <div className="flex items-center mb-6">
                <div className="bg-blue-100 p-3 rounded-full mr-4">
                  <FaUserMd className="text-2xl text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-lg">Dr. Sarah Johnson</h4>
                  <p className="text-sm text-gray-600">Chief Medical Officer</p>
                </div>
              </div>
              <blockquote className="text-gray-700 italic">
                "ClarityDX has transformed our diagnostic workflow, providing
                accurate results in seconds that previously took hours of manual
                analysis."
              </blockquote>
            </div>
          </div>
        </div>

        {/* Testimonials Section */}
        <div className="mt-24 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-12 shadow-sm">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Trusted by Healthcare Professionals
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            <div className="bg-white p-8 rounded-xl shadow-md">
              <div className="flex items-center mb-6">
                <img
                  src="https://images.unsplash.com/photo-1594824476967-48c8b964273f?ixlib=rb-1.2.1&auto=format&fit=crop&w=128&h=128&fit=crop"
                  alt="Dr. Michael Chen"
                  className="w-16 h-16 rounded-full mr-4 object-cover"
                />
                <div>
                  <h4 className="font-semibold text-lg">Dr. Michael Chen</h4>
                  <p className="text-sm text-gray-600">Cardiologist</p>
                </div>
              </div>
              <p className="text-gray-700">
                "The heart disease prediction module has become an indispensable
                tool in our practice, helping us identify at-risk patients
                earlier than traditional methods."
              </p>
            </div>
            <div className="bg-white p-8 rounded-xl shadow-md">
              <div className="flex items-center mb-6">
                <img
                  src="https://images.unsplash.com/photo-1622253692010-333f2da6031d?ixlib=rb-1.2.1&auto=format&fit=crop&w=128&h=128&fit=crop"
                  alt="Dr. Angela Rodriguez"
                  className="w-16 h-16 rounded-full mr-4 object-cover"
                />
                <div>
                  <h4 className="font-semibold text-lg">
                    Dr. Angela Rodriguez
                  </h4>
                  <p className="text-sm text-gray-600">Pathologist</p>
                </div>
              </div>
              <p className="text-gray-700">
                "ClarityDX's malaria detection achieves pathologist-level
                accuracy while reducing analysis time from 30 minutes to under
                10 seconds per slide."
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-20 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Ready to Experience AI-Powered Diagnostics?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Join hundreds of healthcare providers using ClarityDX to enhance
            their diagnostic capabilities
          </p>
          <button className="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl transition-all hover:from-blue-700 hover:to-blue-600">
            Get Started with ClarityDX
          </button>
        </div>
      </div>
    </div>
  );
};

export default About;
