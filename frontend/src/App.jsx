// src/App.jsx
import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import About from "./pages/About";
import Login from "./pages/Login";
import HelpFAQ from "./components/HelpFAQ"; // Changed to page
import HepatitisCDiagnosis from "./components/HepatitisCDiagnosis"; // Changed to page
import MalariaDiagnosis from "./components/MalariaDiagnosis"; // Changed to page
import HeartDiseaseDiagnosis from "./components/HeartDiseaseDiagnosis"; // Changed to page
import KidneyDiseaseDiagnosis from "./components/KidneyDiseaseDiagnosis"; // Changed to page

import { AuthProvider, useAuth } from "./context/AuthContext";
import DiagnosticTools from "./pages/DiagnosticTools"; // Import the component
import EncounterDetails from "./pages/EncounterDetails";
import RecordsPage from "./pages/RecordsPage";

import PatientSelectionPage from "./pages/PatientSelectionPage";
import CreatePatientForm from "./components/CreatePatientForm";
import PatientDetails from "./pages/PatientDetails"; // New page
import Encounters from "./pages/Encounters";
import Reports from "./pages/Reports"; // New page - **Important!**
import SymScanPredictor from "./components/SymScanPredictor";

// Protected Route Component (Keep this as it is)
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
};

// Main App Component
const App = () => {
  const { user } = useAuth();

  return (
    <AuthProvider>
      <Router>
        <div className="flex flex-col min-h-screen">
          {user && <Header />} {/* Show Header only when logged in */}
          <main className="flex-grow">
            <Routes>
              {/* Force login as first screen */}
              <Route path="/login" element={<Login />} />
              <Route
                path="*"
                element={user ? <Home /> : <Navigate to="/login" replace />}
              />
              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Home />
                  </ProtectedRoute>
                }
              />
              <Route path="/diagnosis" element={<DiagnosticTools />} />
              <Route
                path="/about"
                element={
                  <ProtectedRoute>
                    <About />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/help"
                element={
                  <ProtectedRoute>
                    <HelpFAQ />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/symscan"
                element={
                  <ProtectedRoute>
                    <SymScanPredictor />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/malaria-diagnosis"
                element={
                  <ProtectedRoute>
                    <MalariaDiagnosis />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/hepatitis-diagnosis"
                element={
                  <ProtectedRoute>
                    <HepatitisCDiagnosis />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/heart-disease-diagnosis"
                element={
                  <ProtectedRoute>
                    <HeartDiseaseDiagnosis />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/kidney-disease-diagnosis"
                element={
                  <ProtectedRoute>
                    <KidneyDiseaseDiagnosis />
                  </ProtectedRoute>
                }
              />

              {/* New Routes for Patient and Encounter Management */}
              <Route
                path="/patients"
                element={
                  <ProtectedRoute>
                    <PatientSelectionPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/patients/new"
                element={
                  <ProtectedRoute>
                    <CreatePatientForm />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/patients/:patientId"
                element={
                  <ProtectedRoute>
                    <PatientDetails />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/encounters"
                element={
                  <ProtectedRoute>
                    <Encounters />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/patients/:patientId/encounters"
                element={
                  <ProtectedRoute>
                    <Encounters />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/encounters/:encounterId"
                element={<EncounterDetails />}
              />

              {/* New Route for Reports */}
              <Route
                path="/reports"
                element={
                  <ProtectedRoute>
                    <Reports />
                  </ProtectedRoute>
                }
              />

              {/* New Route for Records*/}
              <Route
                path="/records"
                element={
                  <ProtectedRoute>
                    <RecordsPage />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </main>
          {user && <Footer />}
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
