import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom"; // If using React Router
import axios from "axios";
import {
  Card,
  CardContent,
  CardTitle,
  CardDescription,
  Button,
} from "@/components/ui/card"; // Adjust import path
import { BASE_API_URL } from "../utils/apiConfig"; // Ensure this path is correct relative to EncounterList.jsx

function EncounterList() {
  const { patientId } = useParams(); // Get patientId from URL
  const [encounters, setEncounters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEncounters = async () => {
      setLoading(true);
      setError(null);
      try {
        // THIS IS THE CRUCIAL CHANGE: Use BASE_API_URL from environment variables
        const response = await axios.get(
          `${BASE_API_URL}/patients/${patientId}/encounters` // Correctly uses the base URL
        );
        if (response.status === 200) {
          setEncounters(response.data);
        } else if (response.status === 404) {
          setError("No encounters found for this patient.");
        } else {
          throw new Error(
            `Failed to fetch encounters. Status: ${response.status}`
          );
        }
      } catch (err) {
        console.error("Error fetching encounters:", err);
        setError("Could not retrieve encounter history.");
      } finally {
        setLoading(false);
      }
    };

    // Add a check to only fetch if patientId is valid
    if (patientId) {
      fetchEncounters();
    }
  }, [patientId]); // Fetch encounters when patientId changes

  if (loading) {
    return <div>Loading encounter history...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Encounter History</h2>

      {encounters.length === 0 ? (
        <div>No encounters found for this patient.</div>
      ) : (
        encounters.map((encounter) => (
          <Card
            key={encounter.encounter_id}
            className="mb-4 shadow-md hover:shadow-lg transition-shadow duration-300"
          >
            <CardContent className="p-4">
              <CardTitle className="text-lg font-semibold">
                Encounter on {encounter.encounter_date}
              </CardTitle>
              <CardDescription>
                Time: {encounter.encounter_time || "N/A"}
              </CardDescription>
              <CardDescription>
                Chief Complaint: {encounter.chief_complaint || "N/A"}
              </CardDescription>
              <Link to={`/encounters/${encounter.encounter_id}`}>
                <Button size="sm">View Details</Button>
              </Link>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
}

export default EncounterList;
