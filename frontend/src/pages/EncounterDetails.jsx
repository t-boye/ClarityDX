import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import { BASE_API_URL } from "../utils/apiConfig"; // <--- ADD THIS LINE!
// Ensure the path '../utils/apiConfig' is correct relative to this file.

const EncounterDetails = () => {
  const { encounterId } = useParams(); // Get the dynamic ID from the URL
  const [encounter, setEncounter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      // THIS IS THE CRUCIAL CHANGE:
      .get(`${BASE_API_URL}/encounters/${encounterId}`) // <--- UPDATED URL HERE!
      .then((res) => {
        setEncounter(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to fetch encounter.");
        setLoading(false);
        console.error(err);
      });
  }, [encounterId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (!encounter) return <div>No encounter found.</div>;

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Encounter Details</h2>
      <p>
        <strong>Date:</strong> {encounter.encounter_date}
      </p>
      <p>
        <strong>Time:</strong> {encounter.encounter_time}
      </p>
      <p>
        <strong>Chief Complaint:</strong> {encounter.chief_complaint}
      </p>
      <p>
        <strong>Notes:</strong> {encounter.notes}
      </p>
      <p>
        <strong>User ID:</strong> {encounter.user_id || "N/A"}
      </p>
    </div>
  );
};

export default EncounterDetails;
