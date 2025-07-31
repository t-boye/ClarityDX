import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  FaStethoscope,
  FaClinicMedical,
  FaBookMedical,
  FaSearch,
  FaToolbox,
  FaFlask,
  FaHeart,
  FaLaptopMedical,
  FaHistory,
  FaRocket,
} from "react-icons/fa";
import { MdHealthAndSafety } from "react-icons/md";

const availableDiagnosisTools = [
  {
    id: "malaria",
    name: "Malaria Diagnosis",
    href: "/malaria-diagnosis",
    icon: <FaStethoscope className="text-blue-500" />,
    targets: ["malaria", "fever", "parasites", "blood test"],
  },
  {
    id: "hepatitis",
    name: "Hepatitis C Diagnosis",
    href: "/hepatitis-diagnosis",
    icon: <MdHealthAndSafety className="text-green-500" />,
    targets: ["hepatitis c", "liver", "viral infection", "blood panel"],
  },
  {
    id: "heart",
    name: "Heart Disease Prediction",
    href: "/heart-disease-diagnosis",
    icon: <FaHeart className="text-red-500" />,
    targets: ["heart disease", "cardiac", "chest pain", "cholesterol"],
  },
  {
    id: "kidney",
    name: "Kidney Disease Assessment",
    href: "/kidney-disease-diagnosis",
    icon: <FaClinicMedical className="text-purple-500" />,
    targets: ["kidney disease", "renal", "kidney function", "dialysis"],
  },
  {
    id: "diabetes",
    name: "Diabetes Risk Calculator",
    href: "/diabetes-diagnosis",
    icon: <FaFlask className="text-yellow-500" />,
    targets: ["diabetes", "blood sugar", "insulin", "glucose"],
  },
  {
    id: "hypertension",
    name: "Hypertension Monitoring",
    href: "/hypertension-monitoring",
    icon: <FaLaptopMedical className="text-indigo-500" />,
    targets: ["hypertension", "high blood pressure", "bp"],
  },
];

function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [recentToolSearches, setRecentToolSearches] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const savedSearches = localStorage.getItem("recentToolSearches");
    if (savedSearches) {
      setRecentToolSearches(JSON.parse(savedSearches));
    }
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    const matchedTool = availableDiagnosisTools.find(
      (tool) => tool.name.toLowerCase() === searchQuery.toLowerCase()
    );

    if (matchedTool) {
      navigate(matchedTool.href);
    } else {
      const updatedSearches = [
        searchQuery,
        ...recentToolSearches.filter((item) => item !== searchQuery),
      ].slice(0, 5);
      setRecentToolSearches(updatedSearches);
      localStorage.setItem(
        "recentToolSearches",
        JSON.stringify(updatedSearches)
      );
      navigate(`/diagnosis/tools?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const fetchToolSuggestions = (query) => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    setIsSearching(true);
    const lowerQuery = query.toLowerCase();
    const filtered = availableDiagnosisTools
      .filter(
        (tool) =>
          tool.name.toLowerCase().includes(lowerQuery) ||
          tool.targets.some((target) => target.includes(lowerQuery))
      )
      .slice(0, 5);

    setSuggestions(filtered);
    setIsSearching(false);
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    fetchToolSuggestions(value);
  };

  const navigateToTool = (toolHref) => {
    navigate(toolHref);
    setSearchQuery("");
    setSuggestions([]);
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 min-h-screen">
      <div className="flex flex-col items-center">
        {/* Header with improved gradient */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-teal-500 bg-clip-text text-transparent mb-2">
            Diagnosis Tool Finder
          </h1>
          <p className="text-gray-600 max-w-lg">
            Quickly access specialized diagnostic tools for accurate medical
            assessments
          </p>
        </div>

        {/* Enhanced search bar */}
        <form onSubmit={handleSearch} className="w-full max-w-2xl mb-8">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <FaSearch className="text-gray-400" />
            </div>
            <Input
              type="text"
              className="pl-10 pr-10 py-5 text-base rounded-xl shadow-md focus-visible:ring-2 focus-visible:ring-blue-400 border-gray-300"
              placeholder="Search tools (e.g. 'malaria', 'heart disease')..."
              value={searchQuery}
              onChange={handleInputChange}
              autoFocus
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              {isSearching ? (
                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500"></div>
              ) : (
                <FaToolbox className="text-gray-400" />
              )}
            </div>
          </div>

          {/* Suggestions dropdown with better styling */}
          {suggestions.length > 0 && (
            <div className="mt-1 bg-white rounded-lg shadow-lg border border-gray-200 w-full z-10">
              {suggestions.map((tool, index) => (
                <div
                  key={index}
                  className="p-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 flex items-center gap-3 transition-colors"
                  onClick={() => navigateToTool(tool.href)}
                >
                  <div className="text-blue-500">{tool.icon}</div>
                  <div>
                    <p className="font-medium">{tool.name}</p>
                    <p className="text-xs text-gray-500">
                      {tool.targets.slice(0, 2).join(", ")}...
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </form>

        {/* Recent searches card with improved layout */}
        {recentToolSearches.length > 0 && (
          <Card className="w-full max-w-2xl mb-8 shadow-sm">
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <FaHistory className="text-gray-500" />
                <CardTitle className="text-lg">Recent Searches</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="pt-2">
              <div className="flex flex-wrap gap-2">
                {recentToolSearches.map((search, index) => {
                  const toolMatch = availableDiagnosisTools.find(
                    (tool) => tool.name.toLowerCase() === search.toLowerCase()
                  );
                  return (
                    <Button
                      key={index}
                      variant="outline"
                      size="sm"
                      className="rounded-full gap-2"
                      onClick={() => {
                        toolMatch
                          ? navigateToTool(toolMatch.href)
                          : navigate(
                              `/diagnosis/tools?q=${encodeURIComponent(search)}`
                            );
                      }}
                    >
                      <FaSearch className="text-gray-500 text-xs" />
                      {search}
                    </Button>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick actions with better styling */}
        <div className="w-full">
          {/* <h2 className="text-xl font-semibold mb-4">Quick Access</h2> */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Button
              variant="outline"
              className="h-20 flex-col gap-2 hover:bg-blue-50"
              asChild
            >
              <Link to="/diagnosis">
                <FaStethoscope className="text-lg text-white-600" />
                <span className="text-sm">All Diagnosis Tools</span>
              </Link>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-2 hover:bg-green-50"
              asChild
            >
              <Link to="/patients">
                <FaClinicMedical className="text-lg text-green-600" />
                <span className="text-sm">Patient Records</span>
              </Link>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex-col gap-2 hover:bg-purple-50"
              asChild
            >
              <Link to="/knowledge-base">
                <FaBookMedical className="text-lg text-purple-600" />
                <span className="text-sm">Medical Library</span>
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
