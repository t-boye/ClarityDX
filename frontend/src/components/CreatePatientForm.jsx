import React, { useState, useCallback } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function CreatePatientForm({ onPatientCreated }) {
  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "",
    contact_info: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setLoading(true);
      setError("");
      setSuccess(false);

      if (!formData.name.trim()) {
        setError("❌ Name is required.");
        setLoading(false);
        return;
      }
      if (formData.name.length > 255) {
        setError("❌ Name cannot exceed 255 characters.");
        setLoading(false);
        return;
      }
      if (
        formData.age &&
        (isNaN(parseInt(formData.age, 10)) || parseInt(formData.age, 10) < 0)
      ) {
        setError("❌ Age must be a non-negative number.");
        setLoading(false);
        return;
      }
      if (
        formData.gender &&
        !["male", "female", "other"].includes(formData.gender.toLowerCase())
      ) {
        setError("❌ Invalid gender value.");
        setLoading(false);
        return;
      }

      try {
        const response = await axios.post(`${API_BASE_URL}/patients`, {
          name: formData.name,
          age: formData.age ? parseInt(formData.age, 10) : null,
          gender: formData.gender?.toLowerCase() || null,
          contact_info: formData.contact_info,
        });

        if (response.status === 201) {
          setSuccess(true);
          onPatientCreated(response.data.patient);
          setTimeout(() => {
            navigate(`/patients/${response.data.patient.patient_id}`);
          }, 1500); // Redirect after 1.5s to show success message
        } else {
          throw new Error(
            `Failed to create patient. Status: ${response.status}`
          );
        }
      } catch (err) {
        setError(`❌ ${err.response?.data?.error || "An error occurred."}`);
        console.error("Error creating patient:", err);
      } finally {
        setLoading(false);
      }
    },
    [formData, onPatientCreated, navigate]
  );

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-2xl font-bold mb-4 text-center">
        🏥 Add New Patient
      </h3>

      {success && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-md text-center">
          ✅ Patient created successfully! Redirecting...
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name" className="flex items-center gap-1">
            <span>👤</span> Full Name
          </Label>
          <Input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            className="mt-1"
            placeholder="John Doe"
          />
        </div>

        <div>
          <Label htmlFor="age" className="flex items-center gap-1">
            <span>🎂</span> Age
          </Label>
          <Input
            type="number"
            id="age"
            name="age"
            value={formData.age}
            onChange={handleInputChange}
            className="mt-1"
            placeholder="30"
          />
        </div>

        <div>
          <Label htmlFor="gender" className="flex items-center gap-1">
            <span>🚻</span> Gender
          </Label>
          <select
            id="gender"
            name="gender"
            value={formData.gender}
            onChange={handleInputChange}
            className="w-full p-2 border rounded-md mt-1"
          >
            <option value="">Select gender</option>
            <option value="male">Male ♂️</option>
            <option value="female">Female ♀️</option>
            <option value="other">Other ⚧️</option>
          </select>
        </div>

        <div>
          <Label htmlFor="contact_info" className="flex items-center gap-1">
            <span>📞</span> Contact Info
          </Label>
          <Input
            type="text"
            id="contact_info"
            name="contact_info"
            value={formData.contact_info}
            onChange={handleInputChange}
            className="mt-1"
            placeholder="Email or Phone"
          />
        </div>

        <Button type="submit" disabled={loading} className="w-full mt-4">
          {loading ? "⏳ Creating..." : "➕ Create Patient"}
        </Button>
      </form>
    </div>
  );
}

export default CreatePatientForm;
