import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import axios from "axios";

const PatientForm = ({ onPatientCreated }) => {
  const [newPatientData, setNewPatientData] = useState({
    name: "",
    age: "",
    gender: "",
    contact_info: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleInputChange = (e) => {
    setNewPatientData({ ...newPatientData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await axios.post("/api/patients", newPatientData); // Adjust URL
      if (response.status === 201) {
        onPatientCreated(response.data); // Notify parent component
        setNewPatientData({ name: "", age: "", gender: "", contact_info: "" }); // Reset form
      } else {
        throw new Error("Failed to create patient.");
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
      <h3 className="text-lg font-semibold mb-2">Add New Patient</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            type="text"
            id="name"
            name="name"
            value={newPatientData.name}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <Label htmlFor="age">Age</Label>
          <Input
            type="number"
            id="age"
            name="age"
            value={newPatientData.age}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <Label htmlFor="gender">Gender</Label>
          <Input
            type="text"
            id="gender"
            name="gender"
            value={newPatientData.gender}
            onChange={handleInputChange}
          />
        </div>
        <div>
          <Label htmlFor="contact_info">Contact Info</Label>
          <Input
            type="text"
            id="contact_info"
            name="contact_info"
            value={newPatientData.contact_info}
            onChange={handleInputChange}
          />
        </div>
        <Button type="submit" disabled={loading}>
          {loading ? "Creating..." : "Create Patient"}
        </Button>
        {error && <p className="text-red-500">{error}</p>}
      </form>
    </div>
  );
};

export default PatientForm;
