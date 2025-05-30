import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { Search, Plus, Filter, Edit, Trash2, ChevronRight } from "lucide-react";
import { toast } from "sonner"; // Using sonner for toasts (you can use any toast library)

const API_BASE_URL = "http://127.0.0.1:8000/api";

function PatientSelectionPage() {
  const [patients, setPatients] = useState([]);
  const [filteredPatients, setFilteredPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [patientToDelete, setPatientToDelete] = useState(null);
  const navigate = useNavigate();
  const searchInputRef = useRef(null);

  // Custom hook for debouncing
  function useDebounce(value, delay) {
    const [debouncedValue, setDebouncedValue] = useState(value);

    useEffect(() => {
      const handler = setTimeout(() => {
        setDebouncedValue(value);
      }, delay);

      return () => {
        clearTimeout(handler);
      };
    }, [value, delay]);

    return debouncedValue;
  }

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  useEffect(() => {
    const fetchPatients = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`${API_BASE_URL}/patients`);
        if (response.status === 200) {
          setPatients(response.data);
        } else {
          throw new Error(
            `Failed to fetch patients. Status: ${response.status}`
          );
        }
      } catch (err) {
        console.error("Error fetching patients:", err);
        setError("Could not retrieve patient list. Please try again later.");
        toast.error("Failed to load patients");
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  useEffect(() => {
    const results = patients.filter(
      (patient) =>
        patient.name
          .toLowerCase()
          .includes(debouncedSearchTerm.toLowerCase()) ||
        (patient.contact_info &&
          patient.contact_info.includes(debouncedSearchTerm))
    );
    setFilteredPatients(results);
  }, [debouncedSearchTerm, patients]);

  const handlePatientClick = (patientId) => {
    navigate(`/patients/${patientId}`);
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  useEffect(() => {
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, []);

  // CRUD Operations
  const handleEditPatient = (patientId, e) => {
    e.stopPropagation();
    navigate(`/patients/edit/${patientId}`);
  };

  const confirmDeletePatient = (patientId, e) => {
    e.stopPropagation();
    setPatientToDelete(patientId);
    setDeleteDialogOpen(true);
  };

  const handleDeletePatient = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/patients/${patientToDelete}`);
      setPatients(
        patients.filter((patient) => patient.patient_id !== patientToDelete)
      );
      toast.success("Patient deleted successfully");
    } catch (err) {
      toast.error("Failed to delete patient");
      console.error("Error deleting patient:", err);
    } finally {
      setDeleteDialogOpen(false);
      setPatientToDelete(null);
    }
  };

  const getGenderColor = (gender) => {
    switch (gender?.toLowerCase()) {
      case "male":
        return "bg-blue-100 text-blue-800";
      case "female":
        return "bg-pink-100 text-pink-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getInitials = (name) => {
    const nameParts = name.split(" ");
    const initials = nameParts
      .map((part) => part.charAt(0).toUpperCase())
      .join("");
    return initials;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Delete Confirmation Dialog */}
      {deleteDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full">
            <h3 className="text-lg font-bold mb-2">Confirm Delete</h3>
            <p className="mb-4">
              Are you sure you want to delete this patient record?
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setDeleteDialogOpen(false)}
                className="px-4 py-2 border rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleDeletePatient}
                className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
          <h2 className="text-2xl font-bold">Patient Records</h2>
          <p className="text-muted-foreground">
            {loading
              ? "Loading..."
              : `${filteredPatients.length} patients found`}
          </p>
        </div>

        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              placeholder="Search patients..."
              className="pl-9 p-2 border rounded-md w-full"
              value={searchTerm}
              onChange={handleSearch}
              ref={searchInputRef}
            />
          </div>
          <button className="p-2 border rounded-md">
            <Filter className="h-4 w-4" />
          </button>
          <button className="p-2 border rounded-md flex items-center">
            <Link to="/patients/new" className="flex items-center">
              <Plus className="h-4 w-4 mr-2" />
              Add New Patient
            </Link>
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="border p-4 rounded-md animate-pulse">
              <div className="h-6 w-3/4 bg-gray-200 mb-2"></div>
              <div className="h-4 w-1/2 bg-gray-200 mb-2"></div>
              <div className="h-4 w-1/2 bg-gray-200"></div>
            </div>
          ))}
        </div>
      ) : filteredPatients.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 gap-4 text-center">
          <div className="bg-gray-100 p-6 rounded-full">
            <Search className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold">
            {searchTerm
              ? "No matching patients found"
              : "No patients available"}
          </h3>
          <p className="text-muted-foreground max-w-md">
            {searchTerm
              ? "Try adjusting your search or create a new patient record"
              : "Create your first patient record to get started"}
          </p>
          <button className="p-2 border rounded-md flex items-center">
            <Link to="/patients/new" className="flex items-center">
              <Plus className="h-4 w-4 mr-2" />
              Add New Patient
            </Link>
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredPatients.map((patient) => (
            <div
              key={patient.patient_id}
              className="border rounded-md p-4 hover:shadow-md transition-shadow cursor-pointer relative group"
              onClick={() => handlePatientClick(patient.patient_id)}
            >
              <div className="flex items-start gap-3">
                <div
                  className={`w-10 h-10 rounded-full ${getGenderColor(
                    patient.gender
                  )} flex items-center justify-center`}
                >
                  {getInitials(patient.name)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-lg truncate">
                    {patient.name}
                  </div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {patient.age && (
                      <span className="border rounded-md p-1 text-sm">
                        Age: {patient.age}
                      </span>
                    )}
                    {patient.gender && (
                      <span
                        className={`border rounded-md p-1 text-sm ${getGenderColor(
                          patient.gender
                        )}`}
                      >
                        {patient.gender}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {patient.contact_info && (
                <div className="mt-3 text-sm text-muted-foreground truncate">
                  <span className="font-medium">Contact:</span>{" "}
                  {patient.contact_info}
                </div>
              )}

              {/* Action Buttons */}
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                <button
                  onClick={(e) => handleEditPatient(patient.patient_id, e)}
                  className="p-1.5 bg-blue-50 text-blue-600 rounded hover:bg-blue-100"
                  title="Edit"
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => confirmDeletePatient(patient.patient_id, e)}
                  className="p-1.5 bg-red-50 text-red-600 rounded hover:bg-red-100"
                  title="Delete"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="mt-3 flex justify-end">
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PatientSelectionPage;
