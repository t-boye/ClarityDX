import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import axios from "axios";

const EncounterForm = ({ patientId, onEncounterCreated }) => {
  const [newEncounterData, setNewEncounterData] = useState({
    chief_complaint: "",
    notes: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e) => {
    setNewEncounterData({
      ...newEncounterData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/patients/${patientId}/encounters`,
        newEncounterData
      ); // Adjust URL
      if (response.status === 201) {
        onEncounterCreated(response.data);
        setNewEncounterData({
          chief_complaint: "",
          notes: "",
        });
      } else {
        throw new Error("Failed to create encounter.");
      }
    } catch (err) {
      setError(err.message || "An error occurred.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mb-4">
      <h3 className="text-lg font-semibold mb-2">Add New Encounter</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="chief_complaint">Chief Complaint</Label>
          <Input
            type="text"
            id="chief_complaint"
            name="chief_complaint"
            value={newEncounterData.chief_complaint}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <Label htmlFor="notes">Notes</Label>
          <Input
            type="textarea"
            id="notes"
            name="notes"
            value={newEncounterData.notes}
            onChange={handleInputChange}
          />
        </div>
        <Button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Encounter"}
        </Button>
        {error && <p className="text-red-500">{error}</p>}
      </form>
    </div>
  );
};

export default EncounterForm;
