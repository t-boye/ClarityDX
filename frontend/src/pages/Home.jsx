import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios"; // Still good to keep if you later integrate with a backend for tool suggestions
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  FaStethoscope,
  FaClinicMedical,
  FaBookMedical,
  FaSearch,
  FaToolbox, // New icon for tools
  FaFlask, // Another tool-related icon
  FaLaptopMedical, // For AI tools
} from "react-icons/fa";
import { MdHealthAndSafety } from "react-icons/md";
import { BASE_API_URL } from "../utils/apiConfig"; // Keep if you still have other API calls

// Define your available diagnosis tools/services and what they target
const availableDiagnosisTools = [
  {
    id: "malaria",
    name: "Malaria Diagnosis Tool",
    href: "/malaria-diagnosis", // Added href for direct navigation
    targets: ["malaria", "fever", "parasites", "blood test"],
  },
  {
    id: "hepatitis",
    name: "Hepatitis C Diagnosis Tool",
    href: "/hepatitis-diagnosis", // Added href for direct navigation
    targets: ["hepatitis c", "liver", "viral infection", "blood panel"],
  },
  {
    id: "heart",
    name: "Heart Disease Prediction Tool",
    href: "/heart-disease-diagnosis", // Added href for direct navigation
    targets: [
      "heart disease",
      "cardiac",
      "chest pain",
      "cholesterol",
      "blood pressure",
    ],
  },
  {
    id: "kidney",
    name: "Kidney Disease Assessment",
    href: "/kidney-disease-diagnosis", // Added href for direct navigation
    targets: ["kidney disease", "renal", "kidney function", "dialysis"],
  },
  {
    id: "diabetes",
    name: "Diabetes Risk Calculator",
    href: "/diabetes-diagnosis", // Example new href
    targets: ["diabetes", "blood sugar", "insulin", "glucose"],
  },
  {
    id: "hypertension",
    name: "Hypertension Monitoring System",
    href: "/hypertension-monitoring", // Example new href
    targets: ["hypertension", "high blood pressure", "bp", "blood pressure"],
  },
  // Add more tools as needed
];

function Home() {
  const [searchQuery, setSearchQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [recentToolSearches, setRecentToolSearches] = useState([]); // Renamed from recentSearches
  const [isSearching, setIsSearching] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    // Check if the search query exactly matches an available tool name
    const matchedTool = availableDiagnosisTools.find(
      (tool) => tool.name.toLowerCase() === searchQuery.toLowerCase()
    );

    if (matchedTool) {
      // If an exact match, navigate directly to the tool's page
      navigate(matchedTool.href);
    } else {
      // Otherwise, save to recent searches and navigate to a generic search results page
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
    const filteredSuggestions = availableDiagnosisTools
      .filter(
        (tool) =>
          tool.name.toLowerCase().includes(lowerQuery) ||
          tool.targets.some((target) => target.includes(lowerQuery))
      )
      .map((tool) => ({
        name: tool.name, // Keep the full name for display
        href: tool.href, // Add the href for navigation
      }));

    setSuggestions(filteredSuggestions);
    setIsSearching(false);
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    fetchToolSuggestions(value);
  };

  // Function to navigate to a specific tool's page
  const navigateToTool = (toolHref) => {
    navigate(toolHref);
    setSearchQuery(""); // Clear search query after navigation
    setSuggestions([]); // Clear suggestions
  };

  return (
    <div className="max-w-4xl mx-auto py-12 px-4 min-h-screen">
      <div className="flex flex-col items-center justify-center">
        <div className="flex items-center gap-3 mb-8">
          <MdHealthAndSafety className="text-blue-500 text-5xl" />
          <h1 className="text-4xl font-bold text-center bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
            Diagnosis Tool Finder
          </h1>
        </div>

        <form onSubmit={handleSearch} className="w-full max-w-2xl mb-12">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-4 pointer-events-none">
              <FaSearch className="text-gray-400" />
            </div>
            <Input
              type="text"
              className="pl-12 pr-12 py-6 text-lg rounded-full shadow-lg focus-visible:ring-2 focus-visible:ring-blue-500"
              placeholder="Search for diagnosis tools (e.g., 'malaria tool', 'heart disease prediction')..."
              value={searchQuery}
              onChange={handleInputChange}
              autoFocus
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-4">
              {isSearching ? (
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-blue-500"></div>
              ) : (
                <FaToolbox className="text-gray-400" />
              )}
            </div>
          </div>

          {suggestions.length > 0 && (
            <div className="mt-2 bg-white rounded-lg shadow-lg border border-gray-200 w-full">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 flex items-center gap-3"
                  onClick={() => navigateToTool(suggestion.href)} // Navigate directly to the tool's href
                >
                  <FaSearch className="text-gray-400" />
                  <span>{suggestion.name}</span>
                </div>
              ))}
            </div>
          )}
        </form>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
          {/* Recent Tool Searches */}
          {recentToolSearches.length > 0 && (
            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">Recent Tool Searches</CardTitle>{" "}
                {/* Changed title */}
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recentToolSearches.map((search, index) => {
                    const toolMatch = availableDiagnosisTools.find(
                      (tool) => tool.name.toLowerCase() === search.toLowerCase()
                    );
                    return (
                      <Button
                        key={index}
                        variant="ghost"
                        className="w-full justify-start"
                        onClick={() => {
                          if (toolMatch) {
                            navigateToTool(toolMatch.href); // Navigate directly if a match
                          } else {
                            navigate(
                              `/diagnosis/tools?q=${encodeURIComponent(search)}`
                            ); // Fallback to search results
                          }
                        }}
                      >
                        <FaSearch className="mr-2 text-gray-500" />
                        {search}
                      </Button>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Quick Access Cards - These were already good, just keeping them */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8 w-full">
          <Button variant="outline" className="h-24 flex-col gap-2" asChild>
            <Link to="/diagnosis">
              <FaStethoscope className="text-xl" />
              <span>All Diagnosis Tools</span> {/* Changed text for clarity */}
            </Link>
          </Button>
          <Button variant="outline" className="h-24 flex-col gap-2" asChild>
            <Link to="/patients">
              <FaClinicMedical className="text-xl" />
              <span>Patient Records</span>
            </Link>
          </Button>
          <Button variant="outline" className="h-24 flex-col gap-2" asChild>
            <Link to="/knowledge-base">
              <FaBookMedical className="text-xl" />
              <span>Medical Library</span>
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}

export default Home;
