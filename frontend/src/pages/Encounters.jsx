import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom"; // If using React Router
import axios from "axios";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"; // Assuming UI library
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import EncounterForm from "../components/EncounterForm"; // Import the form component
import { BASE_API_URL } from "../utils/apiConfig"; // <--- ADD THIS LINE!
// Ensure the path '../utils/apiConfig' is correct relative to this file.

const Encounters = () => {
  const { patientId } = useParams();
  const [encounters, setEncounters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddEncounterForm, setShowAddEncounterForm] = useState(false);

  useEffect(() => {
    const fetchEncounters = async () => {
      setLoading(true);
      setError(null);
      try {
        // THIS IS THE CRUCIAL CHANGE:
        const response = await axios.get(
          `${BASE_API_URL}/patients/${patientId}/encounters` // <--- UPDATED URL HERE!
        );
        setEncounters(response.data);
      } catch (err) {
        setError(`Could not fetch encounters: ${err.message}`);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchEncounters();
  }, [patientId]);

  const handleToggleForm = () => {
    setShowAddEncounterForm(!showAddEncounterForm);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Encounter History</h2>
      {error && <p className="text-red-500">{error}</p>}
      {loading ? (
        <div>Loading encounters...</div>
      ) : (
        <div>
          <div className="mb-4">
            <Button onClick={handleToggleForm}>
              {showAddEncounterForm ? "Hide Form" : "Add New Encounter"}
            </Button>
          </div>

          {showAddEncounterForm && (
            <EncounterForm
              patientId={patientId}
              onEncounterCreated={() => fetchEncounters()}
            />
          )}

          {encounters.map((encounter) => (
            <Card
              key={encounter.encounter_id}
              className="mb-4 shadow-md hover:shadow-lg transition-shadow duration-200"
            >
              <CardContent>
                <CardTitle>Encounter on {encounter.encounter_date}</CardTitle>
                <CardDescription>
                  Time: {encounter.encounter_time || "N/A"}
                </CardDescription>
                <CardDescription>
                  Chief Complaint: {encounter.chief_complaint || "N/A"}
                </CardDescription>
                <Link to={`/encounters/${encounter.encounter_id}`}>
                  View Details
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Encounters;
