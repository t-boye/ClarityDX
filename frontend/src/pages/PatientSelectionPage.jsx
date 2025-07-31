import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import {
  Search,
  Plus,
  Filter,
  Edit,
  Trash2,
  ChevronRight,
  XCircle,
} from "lucide-react"; // Added XCircle for error icon
import { toast } from "sonner";
import { BASE_API_URL } from "../utils/apiConfig";

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
        const response = await axios.get(`${BASE_API_URL}/patients`);
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
    e.stopPropagation(); // Prevent card click from navigating
    navigate(`/patients/edit/${patientId}`);
  };

  const confirmDeletePatient = (patientId, e) => {
    e.stopPropagation(); // Prevent card click from navigating
    setPatientToDelete(patientId);
    setDeleteDialogOpen(true);
  };

  const handleDeletePatient = async () => {
    try {
      await axios.delete(`${BASE_API_URL}/patients/${patientToDelete}`);
      setPatients(
        patients.filter((patient) => patient.patient_id !== patientToDelete)
      );
      toast.success("Patient record deleted successfully.");
    } catch (err) {
      toast.error("Failed to delete patient record.");
      console.error("Error deleting patient:", err);
    } finally {
      setDeleteDialogOpen(false);
      setPatientToDelete(null);
    }
  };

  const getGenderColor = (gender) => {
    switch (gender?.toLowerCase()) {
      case "male":
        return "bg-blue-500 text-white"; // Stronger blue for initials
      case "female":
        return "bg-pink-500 text-white"; // Stronger pink for initials
      default:
        return "bg-gray-400 text-white"; // Neutral gray for initials
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
    <div className="p-6 max-w-7xl mx-auto min-h-screen bg-gray-50">
      {/* Delete Confirmation Dialog */}
      {deleteDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
          <div className="bg-white p-8 rounded-lg shadow-2xl max-w-sm w-full transform transition-all scale-100 ease-out duration-200">
            <h3 className="text-xl font-bold mb-4 text-gray-800">
              Confirm Deletion
            </h3>
            <p className="mb-6 text-gray-700">
              Are you sure you want to permanently delete this patient record?
              This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setDeleteDialogOpen(false)}
                className="px-5 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeletePatient}
                className="px-5 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-6">
        <div>
          <h2 className="text-4xl font-extrabold text-gray-900 mb-2">
            Patient Records
          </h2>
          <p className="text-lg text-gray-600">
            {loading
              ? "Loading patient data..."
              : filteredPatients.length === patients.length
              ? `Displaying ${filteredPatients.length} patient records.`
              : `Found ${filteredPatients.length} matching patients.`}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <div className="relative flex-grow sm:flex-grow-0 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              placeholder="Search by name or contact..."
              className="pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg w-full focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all shadow-sm"
              value={searchTerm}
              onChange={handleSearch}
              ref={searchInputRef}
            />
          </div>
          {/* Removed Filter button for simplicity, can be added back if filter logic is implemented */}
          {/* <button className="p-2.5 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors flex items-center justify-center">
            <Filter className="h-5 w-5" />
          </button> */}
          <Link
            to="/patients/new"
            className="inline-flex items-center justify-center px-5 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-md"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add New Patient
          </Link>
        </div>
      </div>

      {error && (
        <div
          className="flex items-center bg-red-100 border border-red-300 text-red-800 p-4 rounded-lg mb-8 shadow-sm"
          role="alert"
        >
          <XCircle className="h-6 w-6 mr-3 flex-shrink-0" />
          <p className="font-medium">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div
              key={i}
              className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm animate-pulse"
            >
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-gray-200 flex-shrink-0"></div>
                <div className="flex-1">
                  <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : filteredPatients.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white rounded-lg shadow-md border border-gray-200 text-center mx-auto max-w-xl">
          <div className="bg-blue-50 p-6 rounded-full mb-6">
            <Search className="h-10 w-10 text-blue-500" />
          </div>
          <h3 className="text-2xl font-semibold text-gray-800 mb-3">
            {searchTerm
              ? "No matching patient records found"
              : "No patient records yet"}
          </h3>
          <p className="text-gray-600 mb-8 max-w-md">
            {searchTerm
              ? "Your search did not return any results. Try adjusting your search query or clear the search to see all patients."
              : "It looks like there are no patient records in the system. Start by adding your first patient."}
          </p>
          <Link
            to="/patients/new"
            className="inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-md"
          >
            <Plus className="h-5 w-5 mr-2" />
            Add New Patient
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredPatients.map((patient) => (
            <div
              key={patient.patient_id}
              className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer relative group flex flex-col justify-between"
              onClick={() => handlePatientClick(patient.patient_id)}
            >
              <div className="flex items-start gap-4 mb-4">
                <div
                  className={`w-12 h-12 rounded-full text-lg font-semibold flex items-center justify-center flex-shrink-0 ${getGenderColor(
                    patient.gender
                  )}`}
                >
                  {getInitials(patient.name)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-xl text-gray-800 truncate leading-tight">
                    {patient.name}
                  </div>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {patient.age && (
                      <span className="text-sm bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full font-medium">
                        Age: {patient.age}
                      </span>
                    )}
                    {patient.gender && (
                      <span
                        className={`text-sm px-2 py-0.5 rounded-full font-medium ${
                          patient.gender?.toLowerCase() === "male"
                            ? "bg-blue-100 text-blue-800"
                            : "bg-pink-100 text-pink-800"
                        }`}
                      >
                        {patient.gender}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {patient.contact_info && (
                <div className="text-sm text-gray-600 mt-2 truncate">
                  <span className="font-semibold text-gray-800">Contact:</span>{" "}
                  {patient.contact_info}
                </div>
              )}

              {/* Action Buttons */}
              <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <button
                  onClick={(e) => handleEditPatient(patient.patient_id, e)}
                  className="p-2 bg-blue-50 text-blue-600 rounded-full hover:bg-blue-100 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
                  title="Edit Patient"
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => confirmDeletePatient(patient.patient_id, e)}
                  className="p-2 bg-red-50 text-red-600 rounded-full hover:bg-red-100 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-1"
                  title="Delete Patient"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {/* Chevron icon at bottom right */}
              <div className="mt-4 flex justify-end">
                <ChevronRight className="h-5 w-5 text-gray-400 group-hover:translate-x-1 transition-transform duration-200" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default PatientSelectionPage;
