import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import {
  FaStethoscope,
  FaLungsVirus,
  FaViruses,
  FaHeart,
  FaBrain,
  FaProcedures,
  FaUserMd,
  FaInfoCircle,
  FaQuestionCircle,
} from "react-icons/fa";
import {
  Dialog,
  DialogPanel,
  Popover,
  PopoverButton,
  PopoverGroup,
  PopoverPanel,
} from "@headlessui/react";
import {
  ChevronDownIcon,
  XMarkIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";
import { useAuth } from "../context/AuthContext";
import { getAuth, signOut } from "firebase/auth";
import axios from "axios";

const products = [
  {
    name: "Malaria Diagnosis",
    href: "/malaria-diagnosis",
    icon: FaStethoscope,
    description: "AI-powered malaria detection",
  },
  {
    name: "Hepatitis C Diagnosis",
    href: "/hepatitis-diagnosis",
    icon: FaProcedures,
    description: "Early hepatitis detection system",
  },
  {
    name: "Heart Disease Diagnosis",
    href: "/heart-disease-diagnosis",
    icon: FaHeart,
    description: "Cardiovascular health assessment",
  },
  {
    name: "Kidney Disease Diagnosis",
    href: "/kidney-disease-diagnosis",
    icon: FaProcedures,
    description: "Renal function evaluation",
  },
];

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user } = useAuth();
  const auth = getAuth();
  const navigate = useNavigate();
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPatientDetails = async () => {
      if (patientId) {
        setLoading(true);
        setError(null);
        try {
          const response = await axios.get(`/api/patients/${patientId}`);
          if (response.status === 200) {
            setPatient(response.data);
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
      }
    };

    fetchPatientDetails();
  }, [patientId]);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      navigate("/login");
    } catch (error) {
      console.error("Logout failed", error);
    }
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Top Navigation Bar */}
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0">
              <img
                src="/T-logo-removed.png"
                alt="Logo"
                className="h-8 w-auto"
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex lg:items-center lg:space-x-8">
            <PopoverGroup className="flex space-x-8">
              <Popover className="relative">
                {({ open }) => (
                  <>
                    <PopoverButton className="flex items-center space-x-1 text-sm font-medium text-gray-700 hover:text-indigo-600 focus:outline-none">
                      <span>Services</span>
                      <ChevronDownIcon
                        className={`h-4 w-4 transition-transform ${
                          open ? "rotate-180 transform" : ""
                        }`}
                      />
                    </PopoverButton>
                    <PopoverPanel className="absolute z-10 mt-3 w-64 max-w-md transform px-2 sm:px-0">
                      <div className="overflow-hidden rounded-lg shadow-lg ring-1 ring-black ring-opacity-5">
                        <div className="relative grid gap-6 bg-white p-6">
                          {products.map((item) => (
                            <Link
                              key={item.name}
                              to={item.href}
                              className="-m-3 flex items-start rounded-lg p-3 hover:bg-gray-50 transition duration-150 ease-in-out"
                            >
                              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-md bg-indigo-50 text-indigo-600">
                                <item.icon className="h-6 w-6" />
                              </div>
                              <div className="ml-4">
                                <p className="text-sm font-medium text-gray-900">
                                  {item.name}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {item.description}
                                </p>
                              </div>
                            </Link>
                          ))}
                        </div>
                      </div>
                    </PopoverPanel>
                  </>
                )}
              </Popover>
              <Link
                to="/"
                className="text-sm font-medium text-gray-700 hover:text-indigo-600"
              >
                Home
              </Link>
              <Link
                to="/about"
                className="text-sm font-medium text-gray-700 hover:text-indigo-600"
              >
                About
              </Link>
              <Link
                to="/help"
                className="text-sm font-medium text-gray-700 hover:text-indigo-600"
              >
                FAQ
              </Link>
            </PopoverGroup>
          </div>

          {/* User Actions */}
          <div className="hidden lg:flex lg:items-center lg:space-x-4">
            {user ? (
              <>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                >
                  Logout
                </button>
                {user.photoURL ? (
                  <img
                    src={user.photoURL}
                    alt="User profile"
                    className="h-8 w-8 rounded-full"
                  />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                    <span className="text-indigo-600 text-sm font-medium">
                      {user.email ? user.email.charAt(0).toUpperCase() : "U"}
                    </span>
                  </div>
                )}
              </>
            ) : (
              <div className="flex space-x-4">
                <Link
                  to="/login"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                  Register
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex lg:hidden">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-indigo-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            >
              <span className="sr-only">Open main menu</span>
              <Bars3Icon className="block h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Patient Details (conditionally rendered) */}
        {patient && (
          <div className="bg-indigo-50 p-3 rounded-md mb-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-indigo-800">
                Current Patient
              </h3>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                Active
              </span>
            </div>
            <div className="mt-1 grid grid-cols-2 gap-2">
              <div>
                <p className="text-xs text-gray-500">Name</p>
                <p className="text-sm font-medium text-gray-900">
                  {patient.name || "N/A"}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Age</p>
                <p className="text-sm font-medium text-gray-900">
                  {patient.age || "N/A"}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Gender</p>
                <p className="text-sm font-medium text-gray-900">
                  {patient.gender || "N/A"}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Contact</p>
                <p className="text-sm font-medium text-gray-900">
                  {patient.contact_info || "N/A"}
                </p>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="p-3 bg-blue-50 rounded-md mb-2">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-sm text-blue-800">
                Loading patient details...
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 rounded-md mb-2">
            <div className="flex items-center space-x-2">
              <XMarkIcon className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-800">{error}</span>
            </div>
          </div>
        )}
      </nav>

      {/* Mobile Menu */}
      <Dialog
        as="div"
        className="lg:hidden"
        open={mobileMenuOpen}
        onClose={setMobileMenuOpen}
      >
        <div className="fixed inset-0 z-50" />
        <DialogPanel className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
          <div className="flex items-center justify-between">
            <Link to="/" className="-m-1.5 p-1.5">
              <img className="h-8 w-auto" src="/T-logo-removed.png" alt="" />
            </Link>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-gray-700"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <XMarkIcon className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-6 flow-root">
            <div className="-my-6 divide-y divide-gray-500/10">
              <div className="space-y-2 py-6">
                <div className="-mx-3">
                  <Popover className="relative">
                    {({ open }) => (
                      <>
                        <PopoverButton className="flex w-full items-center justify-between rounded-lg py-2 pl-3 pr-3.5 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50">
                          Services
                          <ChevronDownIcon
                            className={`h-5 w-5 ${open ? "rotate-180" : ""}`}
                          />
                        </PopoverButton>
                        <PopoverPanel className="mt-2 space-y-2">
                          {products.map((item) => (
                            <Link
                              key={item.name}
                              to={item.href}
                              onClick={() => setMobileMenuOpen(false)}
                              className="block rounded-lg py-2 pl-6 pr-3 text-sm font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                            >
                              <div className="flex items-center">
                                <item.icon className="mr-2 h-4 w-4 text-indigo-600" />
                                {item.name}
                              </div>
                            </Link>
                          ))}
                        </PopoverPanel>
                      </>
                    )}
                  </Popover>
                </div>
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                >
                  Home
                </Link>
                <Link
                  to="/about"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                >
                  About
                </Link>
                <Link
                  to="/help"
                  className="text-sm font-medium text-gray-700 hover:text-indigo-600"
                >
                  FAQ
                </Link>
              </div>
              <div className="py-6">
                {user ? (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      {user.photoURL ? (
                        <img
                          src={user.photoURL}
                          alt="User profile"
                          className="h-10 w-10 rounded-full"
                        />
                      ) : (
                        <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                          <span className="text-indigo-600 text-lg font-medium">
                            {user.email
                              ? user.email.charAt(0).toUpperCase()
                              : "U"}
                          </span>
                        </div>
                      )}
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {user.displayName || user.email}
                        </p>
                        <p className="text-xs text-gray-500">Logged in</p>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        handleLogout();
                        setMobileMenuOpen(false);
                      }}
                      className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                    >
                      Logout
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                      Login
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full flex justify-center items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                    >
                      Register
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </DialogPanel>
      </Dialog>
    </header>
  );
};

export default Header;
