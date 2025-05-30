import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom"; // If using React Router
import axios from "axios";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card"; // Assuming UI library
import { Button } from "@/components/ui/button"; // Assuming you have Button component
import {
  FaUser,
  FaPhone,
  FaVenusMars,
  FaBirthdayCake,
  FaNotesMedical,
  FaStethoscope,
  FaHistory,
  FaPlus,
  FaArrowLeft,
  FaSpinner, // Add this import,
} from "react-icons/fa";
import { GiHealthNormal } from "react-icons/gi";
import { MdSick, MdHealthAndSafety } from "react-icons/md";
import { toast } from "react-toastify"; // You'll need to install react-toastify

const PatientDetails = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [creatingEncounter, setCreatingEncounter] = useState(false); // Track encounter creation

  useEffect(() => {
    const fetchPatientDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/api/patients/${patientId}` // Adjust URL
        );
        if (response.status === 200) {
          setPatient(response.data);
        } else if (response.status === 404) {
          setError("Patient not found.");
        } else {
          throw new Error(
            `Failed to fetch patient details: ${response.status}`
          );
        }
      } catch (err) {
        setError(`Could not fetch patient details: ${err.message}`);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPatientDetails();
  }, [patientId]);

  const handleStartDiagnosis = async () => {
    setCreatingEncounter(true);
    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/patients/${patientId}/encounters`,
        {
          encounter_date: new Date().toISOString().split("T")[0], // YYYY-MM-DD
          encounter_type: "diagnosis", // Or whatever type you need
          status: "in-progress", // Or initial status
        }
      );

      if (response.status === 201) {
        toast.success("New diagnosis session started!");
        navigate(`/encounters/${response.data.encounter_id}`); // Navigate to encounter details
      } else {
        throw new Error(`Failed to create encounter: ${response.status}`);
      }
    } catch (err) {
      setError(`Could not start diagnosis: ${err.message}`);
      console.error(err);
    } finally {
      setCreatingEncounter(false);
    }
  };

  if (loading)
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );

  if (error)
    return (
      <div className="text-red-500 p-4 bg-red-50 rounded-lg flex items-center gap-2">
        <MdSick className="text-xl" />
        {error}
      </div>
    );

  if (!patient) return <div>Patient not found.</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <Button asChild variant="outline" className="gap-2">
          <Link to="/patients">
            <FaArrowLeft /> Back to Patients
          </Link>
        </Button>
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <MdHealthAndSafety className="text-blue-500" />
          Patient Details
        </h2>
        <div></div> {/* Spacer for alignment */}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Patient Information Card */}
        <Card className="shadow-md md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FaUser className="text-blue-500" />
              {patient.name}
            </CardTitle>
            <CardDescription className="flex items-center gap-2">
              <GiHealthNormal />
              Patient ID: {patient.patient_id}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              <FaBirthdayCake className="text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">Age</p>
                <p>{patient.age || "N/A"}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <FaVenusMars className="text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">Gender</p>
                <p>{patient.gender || "N/A"}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <FaPhone className="text-gray-500" />
              <div>
                <p className="text-sm text-gray-500">Contact Info</p>
                <p>{patient.contact_info || "N/A"}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions Card */}
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FaStethoscope className="text-green-500" />
              Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              onClick={handleStartDiagnosis}
              disabled={loading || creatingEncounter}
              className="w-full gap-2"
            >
              {creatingEncounter ? (
                <>
                  <FaSpinner className="animate-spin" />
                  Starting Diagnosis...
                </>
              ) : (
                <>
                  <FaPlus /> Start Diagnosis
                </>
              )}
            </Button>

            <Button asChild variant="outline" className="w-full gap-2">
              <Link to={`/patients/${patientId}/encounters`}>
                <FaHistory /> View Encounters
              </Link>
            </Button>

            <Button asChild variant="outline" className="w-full gap-2">
              <Link to={`/patients/${patientId}/edit`}>
                <FaUser /> Edit Patient
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* You could add more sections here to display related data, like allergies, medications, etc. */}
    </div>
  );
};

export default PatientDetails;
