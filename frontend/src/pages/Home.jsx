import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  FaUserMd,
  FaNotesMedical,
  FaListAlt,
  FaStethoscope,
  FaHeart,
  FaUserInjured,
  FaProcedures,
  FaPlus,
  FaSearch,
} from "react-icons/fa";
import { GiHealthNormal } from "react-icons/gi";
import { MdSick, MdHealthAndSafety } from "react-icons/md";
import { BASE_API_URL } from "../utils/apiConfig"; // Ensure this path is correct

function Home() {
  const [patients, setPatients] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(true);
  const [errorPatients, setErrorPatients] = useState(null);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchPatients = async () => {
      setLoadingPatients(true);
      setErrorPatients(null);
      try {
        const response = await axios.get(`${BASE_API_URL}/patients`); // Use BASE_API_URL here
        setPatients(response.data);
      } catch (error) {
        console.error("Error fetching patients:", error);
        setErrorPatients("Could not retrieve patient list.");
      } finally {
        setLoadingPatients(false);
      }
    };

    fetchPatients();
  }, []);

  const handlePatientClick = (patientId) => {
    setSelectedPatientId(patientId);
    navigate(`/patients/${patientId}`);
  };

  const filteredPatients = patients.filter((patient) =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center flex items-center justify-center gap-3">
        <MdHealthAndSafety className="text-blue-500 text-4xl" />
        Multi-Disease Diagnostic System
        <MdHealthAndSafety className="text-blue-500 text-4xl" />
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Diagnosis Tools Card */}
        <Card className="shadow-md hover:shadow-lg transition-shadow duration-300">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <FaStethoscope className="text-blue-500" />
              Diagnosis Tools
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription className="flex items-center gap-2 mb-4">
              <MdSick className="text-xl" />
              Access various diagnostic tools for different diseases
            </CardDescription>
            <Button asChild className="w-full">
              <Link to="/diseases" className="flex items-center gap-2">
                <FaSearch /> Start Diagnosis
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Patient Management Card - Larger on big screens */}
        <Card className="shadow-md hover:shadow-lg transition-shadow duration-300 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-xl font-semibold flex items-center gap-2">
              <FaUserInjured className="text-green-500 text-2xl" />
              Patient Management
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription className="flex items-center gap-2 mb-4">
              <GiHealthNormal className="text-xl" />
              Select or search for a patient to view and manage their records
            </CardDescription>

            <div className="mb-4 flex gap-2">
              <div className="relative flex-grow">
                <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search patients..."
                  className="pl-10 pr-4 py-2 w-full border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button asChild>
                <Link to="/patients/new" className="flex items-center gap-2">
                  <FaPlus /> New
                </Link>
              </Button>
            </div>

            {loadingPatients ? (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            ) : errorPatients ? (
              <div className="text-red-500 p-4 bg-red-50 rounded-lg flex items-center gap-2">
                <FaNotesMedical />
                {errorPatients}
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto">
                {filteredPatients.length === 0 ? (
                  <div className="text-center p-4 text-gray-500">
                    {searchTerm
                      ? "No matching patients found"
                      : "No patients available"}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {filteredPatients.map((patient) => (
                      <div
                        key={patient.patient_id}
                        className={`p-4 rounded-lg border hover:bg-blue-50 cursor-pointer transition-colors flex items-center gap-3 ${
                          selectedPatientId === patient.patient_id
                            ? "bg-blue-100 border-blue-300"
                            : ""
                        }`}
                        onClick={() => handlePatientClick(patient.patient_id)}
                      >
                        <div className="bg-blue-100 p-3 rounded-full">
                          <FaUserInjured className="text-blue-500" />
                        </div>
                        <div>
                          <h3 className="font-medium">{patient.name}</h3>
                          <p className="text-sm text-gray-500">
                            ID: {patient.patient_id}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div className="mt-4 flex justify-between">
              <Button asChild variant="outline">
                <Link to="/patients" className="flex items-center gap-2">
                  <FaListAlt /> View All Patients
                </Link>
              </Button>
              <Button asChild>
                <Link to="/patients/new" className="flex items-center gap-2">
                  <FaPlus /> Add New Patient
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {selectedPatientId && (
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <FaUserInjured className="text-green-500" />
            Selected Patient:{" "}
            {patients.find((p) => p.patient_id === selectedPatientId)?.name}
          </h2>
        </div>
      )}
    </div>
  );
}

export default Home;
