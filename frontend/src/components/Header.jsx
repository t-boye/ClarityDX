import React, { useState, useEffect, Fragment } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import axios from "axios";

// Headless UI imports
import {
  Dialog,
  DialogPanel,
  Popover,
  PopoverButton,
  PopoverGroup,
  PopoverPanel,
  Menu,
  MenuButton,
  MenuItems,
  MenuItem,
  Transition,
} from "@headlessui/react";

// Icon imports
import {
  FaStethoscope,
  FaProcedures,
  FaHeart,
  FaUser,
  FaSignOutAlt,
  FaCog,
  FaBars,
  FaTimes,
  FaChevronDown,
  FaHome,
  FaQuestionCircle,
} from "react-icons/fa";

// Firebase and Context imports
import { getAuth, signOut } from "firebase/auth";
import { useAuth } from "../context/AuthContext";

// Utility function for conditional class names
function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

// Navigation Data Categorized
const imageProcessingItems = [
  {
    name: "Malaria Diagnosis",
    href: "/malaria-diagnosis",
    icon: FaStethoscope,
    description: "AI-powered malaria detection",
    badge: "AI",
  },
];

const syscanItems = [
  {
    name: "Syscan Diagnosis",
    href: "/symscan",
    icon: FaHeart,
    description: "System scan diagnostics",
    badge: "NEW",
  },
];

const textBasedItems = [
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
  // State Management
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Hooks
  const { user } = useAuth();
  const auth = getAuth();
  const navigate = useNavigate();
  const { patientId } = useParams();

  // Effects
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

  // Handlers
  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await signOut(auth);
      navigate("/login");
    } catch (error) {
      console.error("Logout failed", error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50 border-b border-gray-100">
      <nav className="mx-auto max-w-5xl px-3 sm:px-4 lg:px-6">
        {/* Top Navigation Bar */}
        <div className="flex h-14 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <img
                src="https://i.postimg.cc/wxJ7TKPg/clarity.png"
                alt="ClarityDX Logo"
                className="h-14 w-auto mr-2"
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex lg:items-center lg:space-x-6">
            <PopoverGroup className="flex space-x-6">
              {/* Home Link */}
              <Link
                to="/"
                className="flex items-center text-base font-medium text-gray-700 hover:text-blue-600 transition-colors group"
              >
                <FaHome className="mr-2 text-gray-500 group-hover:text-blue-600 text-sm" />
                Home
              </Link>

              <Popover className="relative">
                {({ open }) => (
                  <>
                    <PopoverButton
                      className={classNames(
                        open ? "text-blue-600" : "text-gray-700",
                        "group inline-flex items-center rounded-md text-base font-medium hover:text-blue-600 focus:outline-none transition-colors"
                      )}
                    >
                      <span>Services</span>
                      <FaChevronDown
                        className={classNames(
                          open ? "rotate-180 text-blue-600" : "text-gray-500",
                          "ml-1 h-4 w-4 transition-transform"
                        )}
                        aria-hidden="true"
                      />
                    </PopoverButton>

                    <PopoverPanel className="absolute left-1/2 z-10 mt-2 w-screen max-w-md -translate-x-1/2 transform px-2 sm:px-0">
                      <div className="overflow-hidden rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 bg-white p-3 space-y-4 border border-gray-100">
                        {imageProcessingItems.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-blue-600 mb-2">
                              Image Processing Diagnosis
                            </h4>
                            <div className="grid gap-3">
                              {imageProcessingItems.map((item) => (
                                <Link
                                  key={item.name}
                                  to={item.href}
                                  className="flex items-start p-2 rounded-lg hover:bg-blue-50 transition duration-150 ease-in-out group"
                                >
                                  <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-lg bg-blue-100 text-blue-600 group-hover:bg-blue-200">
                                    <item.icon
                                      className="h-5 w-5"
                                      aria-hidden="true"
                                    />
                                  </div>
                                  <div className="ml-3">
                                    <div className="flex items-center">
                                      <p className="text-sm font-medium text-gray-900">
                                        {item.name}
                                      </p>
                                      {item.badge && (
                                        <span className="ml-1 inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                          {item.badge}
                                        </span>
                                      )}
                                    </div>
                                    <p className="mt-0.5 text-xs text-gray-600">
                                      {item.description}
                                    </p>
                                  </div>
                                </Link>
                              ))}
                            </div>
                          </div>
                        )}

                        {syscanItems.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-blue-600 mb-2">
                              System Scan Diagnosis
                            </h4>
                            <div className="grid gap-3">
                              {syscanItems.map((item) => (
                                <Link
                                  key={item.name}
                                  to={item.href}
                                  className="flex items-start p-2 rounded-lg hover:bg-blue-50 transition duration-150 ease-in-out group"
                                >
                                  <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-lg bg-blue-100 text-blue-600 group-hover:bg-blue-200">
                                    <item.icon
                                      className="h-5 w-5"
                                      aria-hidden="true"
                                    />
                                  </div>
                                  <div className="ml-3">
                                    <div className="flex items-center">
                                      <p className="text-sm font-medium text-gray-900">
                                        {item.name}
                                      </p>
                                      {item.badge && (
                                        <span className="ml-1 inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                          {item.badge}
                                        </span>
                                      )}
                                    </div>
                                    <p className="mt-0.5 text-xs text-gray-600">
                                      {item.description}
                                    </p>
                                  </div>
                                </Link>
                              ))}
                            </div>
                          </div>
                        )}

                        {textBasedItems.length > 0 && (
                          <div>
                            <h4 className="text-xs font-semibold uppercase tracking-wider text-blue-600 mb-2">
                              Text-Based Diagnosis
                            </h4>
                            <div className="grid gap-3">
                              {textBasedItems.map((item) => (
                                <Link
                                  key={item.name}
                                  to={item.href}
                                  className="flex items-start p-2 rounded-lg hover:bg-blue-50 transition duration-150 ease-in-out group"
                                >
                                  <div className="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-lg bg-blue-100 text-blue-600 group-hover:bg-blue-200">
                                    <item.icon
                                      className="h-5 w-5"
                                      aria-hidden="true"
                                    />
                                  </div>
                                  <div className="ml-3">
                                    <p className="text-sm font-medium text-gray-900">
                                      {item.name}
                                    </p>
                                    <p className="mt-0.5 text-xs text-gray-600">
                                      {item.description}
                                    </p>
                                  </div>
                                </Link>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </PopoverPanel>
                  </>
                )}
              </Popover>

              <Link
                to="/about"
                className="text-base font-medium text-gray-700 hover:text-blue-600 transition-colors"
              >
                About
              </Link>

              <Link
                to="/help"
                className="flex items-center text-base font-medium text-gray-700 hover:text-blue-600 transition-colors group"
              >
                <FaQuestionCircle className="mr-2 text-gray-500 group-hover:text-blue-600 text-sm" />
                FAQ
              </Link>
            </PopoverGroup>
          </div>

          {/* User Profile Dropdown */}
          <div className="hidden lg:flex lg:items-center lg:space-x-3">
            {user ? (
              <>
                <Menu as="div" className="relative">
                  <div>
                    <MenuButton className="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                      <span className="sr-only">Open user menu</span>
                      {user.photoURL ? (
                        <img
                          className="h-8 w-8 rounded-full"
                          src={user.photoURL}
                          alt="User profile"
                        />
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-sm">
                            {user.email?.charAt(0).toUpperCase() || "U"}
                          </span>
                        </div>
                      )}
                    </MenuButton>
                  </div>
                  <Transition
                    as={Fragment}
                    enter="transition ease-out duration-200"
                    enterFrom="transform opacity-0 scale-95"
                    enterTo="transform opacity-100 scale-100"
                    leave="transition ease-in duration-75"
                    leaveFrom="transform opacity-100 scale-100"
                    leaveTo="transform opacity-0 scale-95"
                  >
                    <MenuItems className="absolute right-0 mt-2 w-48 origin-top-right rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none divide-y divide-gray-100 z-50 border border-gray-100">
                      <div className="px-3 py-2">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {user.displayName || "User"}
                        </p>
                        <p className="text-xs text-gray-500 truncate">
                          {user.email}
                        </p>
                      </div>
                      <div className="py-1">
                        <MenuItem>
                          {({ active }) => (
                            <Link
                              to="/profile"
                              className={classNames(
                                active
                                  ? "bg-blue-50 text-blue-600"
                                  : "text-gray-700",
                                "flex px-3 py-2 text-sm items-center w-full"
                              )}
                            >
                              <FaUser className="mr-2 h-4 w-4 text-blue-500" />
                              Your Profile
                            </Link>
                          )}
                        </MenuItem>
                        <MenuItem>
                          {({ active }) => (
                            <Link
                              to="/settings"
                              className={classNames(
                                active
                                  ? "bg-blue-50 text-blue-600"
                                  : "text-gray-700",
                                "flex px-3 py-2 text-sm items-center w-full"
                              )}
                            >
                              <FaCog className="mr-2 h-4 w-4 text-blue-500" />
                              Settings
                            </Link>
                          )}
                        </MenuItem>
                      </div>
                      <div className="py-1">
                        <MenuItem>
                          {({ active }) => (
                            <button
                              onClick={handleLogout}
                              disabled={isLoggingOut}
                              className={classNames(
                                active
                                  ? "bg-blue-50 text-blue-600"
                                  : "text-gray-700",
                                "flex px-3 py-2 text-sm items-center w-full"
                              )}
                            >
                              {isLoggingOut ? (
                                <>
                                  <div className="mr-2 h-4 w-4 border-t-2 border-b-2 border-blue-500 rounded-full animate-spin" />
                                  Signing out...
                                </>
                              ) : (
                                <>
                                  <FaSignOutAlt className="mr-2 h-4 w-4 text-blue-500" />
                                  Sign out
                                </>
                              )}
                            </button>
                          )}
                        </MenuItem>
                      </div>
                    </MenuItems>
                  </Transition>
                </Menu>
              </>
            ) : (
              <div className="flex space-x-3">
                <Link
                  to="/login"
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-blue-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
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
              className="inline-flex items-center justify-center p-1.5 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-100 transition-all"
              aria-label="Open main menu"
            >
              <FaBars className="block h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </div>

        {/* Patient Details Section */}
        {patientId && (loading || error || patient) && (
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-2 rounded-lg mb-2 mt-1 shadow-sm border border-blue-100">
            {loading && (
              <div className="flex items-center space-x-2 text-blue-800">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span className="text-sm font-medium">
                  Loading patient details...
                </span>
              </div>
            )}
            {error && (
              <div className="flex items-center space-x-2 text-red-600">
                <FaTimes className="h-4 w-4" aria-hidden="true" />
                <span className="text-sm font-medium">{error}</span>
              </div>
            )}
            {patient && !loading && !error && (
              <>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-base font-semibold text-blue-800 flex items-center">
                    <FaUser className="mr-1 text-blue-600 text-sm" />
                    Current Patient
                  </h3>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Active
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-white p-2 rounded shadow-xs">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </p>
                    <p className="text-sm font-medium text-gray-900">
                      {patient.name || "N/A"}
                    </p>
                  </div>
                  <div className="bg-white p-2 rounded shadow-xs">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Age
                    </p>
                    <p className="text-sm font-medium text-gray-900">
                      {patient.age || "N/A"}
                    </p>
                  </div>
                  <div className="bg-white p-2 rounded shadow-xs">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Gender
                    </p>
                    <p className="text-sm font-medium text-gray-900">
                      {patient.gender || "N/A"}
                    </p>
                  </div>
                  <div className="bg-white p-2 rounded shadow-xs">
                    <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </p>
                    <p className="text-sm font-medium text-gray-900">
                      {patient.contact_info || "N/A"}
                    </p>
                  </div>
                </div>
              </>
            )}
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
        <div className="fixed inset-0 z-50 bg-black bg-opacity-30 backdrop-blur-sm" />
        <DialogPanel className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white px-4 py-4 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
          <div className="flex items-center justify-between">
            <Link
              to="/"
              className="-m-1 p-1 flex items-center"
              onClick={() => setMobileMenuOpen(false)}
            >
              <img
                className="h-8 w-auto mr-2"
                src="https://i.postimg.cc/wxJ7TKPg/clarity.png"
                alt="ClarityDX Logo"
              />
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-500 bg-clip-text text-transparent">
                ClarityDX
              </span>
            </Link>
            <button
              type="button"
              className="-m-1.5 rounded-md p-1.5 text-gray-700 hover:text-blue-600 hover:bg-gray-50 transition-colors"
              onClick={() => setMobileMenuOpen(false)}
              aria-label="Close menu"
            >
              <FaTimes className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-6 flow-root">
            <div className="-my-4 divide-y divide-gray-200">
              <div className="space-y-2 py-4">
                {/* Home Link */}
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-2 flex items-center rounded-lg px-2 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50 transition-colors"
                >
                  <FaHome className="mr-2 text-blue-600 text-sm" />
                  Home
                </Link>

                <Popover className="relative">
                  {({ open }) => (
                    <>
                      <PopoverButton
                        className={classNames(
                          open ? "text-blue-600 bg-gray-50" : "text-gray-900",
                          "flex w-full items-center justify-between rounded-lg py-2 pl-2 pr-2.5 text-base font-semibold leading-7 hover:bg-gray-50 transition-colors"
                        )}
                      >
                        <div className="flex items-center">
                          <FaStethoscope className="mr-2 text-blue-600 text-sm" />
                          Services
                        </div>
                        <FaChevronDown
                          className={classNames(
                            open ? "rotate-180 text-blue-600" : "text-gray-500",
                            "h-4 w-4 flex-none"
                          )}
                          aria-hidden="true"
                        />
                      </PopoverButton>
                      <PopoverPanel className="mt-1 space-y-2 pl-8">
                        {imageProcessingItems.length > 0 && (
                          <div>
                            <h4 className="text-blue-600 font-semibold text-xs uppercase tracking-wider mb-1">
                              Image Processing
                            </h4>
                            {imageProcessingItems.map((item) => (
                              <Link
                                key={item.name}
                                to={item.href}
                                onClick={() => setMobileMenuOpen(false)}
                                className="block rounded-lg py-2 pl-3 pr-2 text-sm font-semibold leading-7 text-gray-900 hover:bg-blue-50 transition-colors"
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center">
                                    <item.icon
                                      className="mr-2 h-4 w-4 text-blue-600"
                                      aria-hidden="true"
                                    />
                                    {item.name}
                                  </div>
                                  {item.badge && (
                                    <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                      {item.badge}
                                    </span>
                                  )}
                                </div>
                              </Link>
                            ))}
                          </div>
                        )}

                        {syscanItems.length > 0 && (
                          <div>
                            <h4 className="text-blue-600 font-semibold text-xs uppercase tracking-wider mb-1">
                              System Scan
                            </h4>
                            {syscanItems.map((item) => (
                              <Link
                                key={item.name}
                                to={item.href}
                                onClick={() => setMobileMenuOpen(false)}
                                className="block rounded-lg py-2 pl-3 pr-2 text-sm font-semibold leading-7 text-gray-900 hover:bg-blue-50 transition-colors"
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center">
                                    <item.icon
                                      className="mr-2 h-4 w-4 text-blue-600"
                                      aria-hidden="true"
                                    />
                                    {item.name}
                                  </div>
                                  {item.badge && (
                                    <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                      {item.badge}
                                    </span>
                                  )}
                                </div>
                              </Link>
                            ))}
                          </div>
                        )}

                        {textBasedItems.length > 0 && (
                          <div>
                            <h4 className="text-blue-600 font-semibold text-xs uppercase tracking-wider mb-1">
                              Text-Based
                            </h4>
                            {textBasedItems.map((item) => (
                              <Link
                                key={item.name}
                                to={item.href}
                                onClick={() => setMobileMenuOpen(false)}
                                className="block rounded-lg py-2 pl-3 pr-2 text-sm font-semibold leading-7 text-gray-900 hover:bg-blue-50 transition-colors"
                              >
                                <div className="flex items-center">
                                  <item.icon
                                    className="mr-2 h-4 w-4 text-blue-600"
                                    aria-hidden="true"
                                  />
                                  {item.name}
                                </div>
                              </Link>
                            ))}
                          </div>
                        )}
                      </PopoverPanel>
                    </>
                  )}
                </Popover>

                <Link
                  to="/about"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-2 flex items-center rounded-lg px-2 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50 transition-colors"
                >
                  <FaUser className="mr-2 text-blue-600 text-sm" />
                  About
                </Link>

                <Link
                  to="/help"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-2 flex items-center rounded-lg px-2 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50 transition-colors"
                >
                  <FaQuestionCircle className="mr-2 text-blue-600 text-sm" />
                  FAQ
                </Link>
              </div>

              <div className="py-4">
                {user ? (
                  <div className="space-y-3">
                    <div className="flex items-center px-2 py-2 rounded-lg bg-gray-50">
                      {user.photoURL ? (
                        <img
                          className="h-10 w-10 rounded-full"
                          src={user.photoURL}
                          alt="User profile"
                        />
                      ) : (
                        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                          <span className="text-blue-600 font-medium text-base">
                            {user.email?.charAt(0).toUpperCase() || "U"}
                          </span>
                        </div>
                      )}
                      <div className="ml-3">
                        <p className="text-sm font-medium text-gray-800">
                          {user.displayName || "User"}
                        </p>
                        <p className="text-xs font-medium text-gray-500">
                          {user.email}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-1">
                      <Link
                        to="/profile"
                        onClick={() => setMobileMenuOpen(false)}
                        className="flex items-center px-2 py-2 text-sm font-medium text-gray-700 hover:bg-blue-50 rounded-md"
                      >
                        <FaUser className="mr-2 h-4 w-4 text-blue-600" />
                        Your Profile
                      </Link>

                      <Link
                        to="/settings"
                        onClick={() => setMobileMenuOpen(false)}
                        className="flex items-center px-2 py-2 text-sm font-medium text-gray-700 hover:bg-blue-50 rounded-md"
                      >
                        <FaCog className="mr-2 h-4 w-4 text-blue-600" />
                        Settings
                      </Link>

                      <button
                        onClick={() => {
                          handleLogout();
                          setMobileMenuOpen(false);
                        }}
                        disabled={isLoggingOut}
                        className="flex items-center px-2 py-2 text-sm font-medium text-gray-700 hover:bg-blue-50 rounded-md w-full"
                      >
                        {isLoggingOut ? (
                          <>
                            <div className="mr-2 h-4 w-4 border-t-2 border-b-2 border-blue-500 rounded-full animate-spin" />
                            Signing out...
                          </>
                        ) : (
                          <>
                            <FaSignOutAlt
                              className="mr-2 h-4 w-4 text-blue-600"
                              aria-hidden="true"
                            />
                            Sign out
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full flex justify-center items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
                    >
                      Login
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full flex justify-center items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-blue-600 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
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
