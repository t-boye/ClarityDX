import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Card,
  CardContent,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"; // Adjust import path
import { BASE_API_URL } from "../utils/apiConfig"; // <--- ADD THIS LINE!
// Ensure the path '../utils/apiConfig' is correct relative to this file.

function PatientsList({ onPatientClick }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPatients = async () => {
      setLoading(true);
      setError(null);
      try {
        // THIS IS THE CRUCIAL CHANGE:
        const response = await axios.get(`${BASE_API_URL}/patients`); // <--- UPDATED URL HERE!
        if (response.status === 200) {
          setPatients(response.data);
        } else {
          throw new Error(
            `Failed to fetch patients. Status: ${response.status}`
          );
        }
      } catch (err) {
        console.error("Error fetching patients:", err);
        setError("Could not retrieve patient list.");
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  if (loading) {
    return <div>Loading patients...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {patients.length === 0 ? (
          <div>No patients found.</div>
        ) : (
          patients.map((patient) => (
            <Card
              key={patient.patient_id}
              className="cursor-pointer hover:shadow-lg transition-shadow duration-300"
              onClick={() => onPatientClick(patient.patient_id)}
            >
              <CardContent className="p-4">
                <CardTitle className="mb-2">{patient.name}</CardTitle>
                <CardDescription>Age: {patient.age || "N/A"}</CardDescription>
                <CardDescription>
                  Gender: {patient.gender || "N/A"}
                </CardDescription>
                <CardDescription>
                  Contact: {patient.contact_info || "N/A"}
                </CardDescription>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

export default PatientsList;
