import React, { useState, useEffect, Fragment } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
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
} from "react-icons/fa";
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
import { useAuth } from "../context/AuthContext";
import { getAuth, signOut } from "firebase/auth";
import axios from "axios";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

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
  const [isLoggingOut, setIsLoggingOut] = useState(false);
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
    <header className="bg-white shadow-md sticky top-0 z-50">
      <nav className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        {/* Top Navigation Bar */}
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0">
              <img
                src="/T-logo-removed.png"
                alt="Your Logo"
                className="h-9 w-auto"
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex lg:items-center lg:space-x-8">
            <PopoverGroup className="flex space-x-8">
              <Popover className="relative">
                {({ open }) => (
                  <>
                    <PopoverButton
                      className={classNames(
                        open ? "text-indigo-600" : "text-gray-700",
                        "group inline-flex items-center rounded-md bg-white text-base font-medium hover:text-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
                      )}
                    >
                      <span>Services</span>
                      <FaChevronDown
                        className={classNames(
                          open ? "text-indigo-600 rotate-180" : "text-gray-400",
                          "ml-2 h-4 w-4 transition-transform group-hover:text-indigo-600"
                        )}
                        aria-hidden="true"
                      />
                    </PopoverButton>
                    <PopoverPanel className="absolute left-1/2 z-10 mt-3 w-screen max-w-md -translate-x-1/2 transform px-2 sm:px-0">
                      <div className="overflow-hidden rounded-lg shadow-lg ring-1 ring-black ring-opacity-5">
                        <div className="relative grid gap-6 bg-white p-6">
                          {products.map((item) => (
                            <Link
                              key={item.name}
                              to={item.href}
                              className="-m-3 flex items-start rounded-lg p-3 hover:bg-gray-50 transition duration-150 ease-in-out"
                            >
                              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-md bg-indigo-50 text-indigo-600 sm:h-12 sm:w-12">
                                <item.icon
                                  className="h-6 w-6"
                                  aria-hidden="true"
                                />
                              </div>
                              <div className="ml-4">
                                <p className="text-base font-medium text-gray-900">
                                  {item.name}
                                </p>
                                <p className="mt-1 text-sm text-gray-500">
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
                className="text-base font-medium text-gray-700 hover:text-indigo-600 transition-colors"
              >
                Home
              </Link>
              <Link
                to="/about"
                className="text-base font-medium text-gray-700 hover:text-indigo-600 transition-colors"
              >
                About
              </Link>
              <Link
                to="/help"
                className="text-base font-medium text-gray-700 hover:text-indigo-600 transition-colors"
              >
                FAQ
              </Link>
            </PopoverGroup>
          </div>

          {/* User Profile Dropdown */}
          <div className="hidden lg:flex lg:items-center">
            {user ? (
              <Menu as="div" className="relative ml-4">
                <div>
                  <MenuButton className="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                    <span className="sr-only">Open user menu</span>
                    {user.photoURL ? (
                      <img
                        className="h-8 w-8 rounded-full"
                        src={user.photoURL}
                        alt="User profile"
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                        <span className="text-indigo-600 font-medium">
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
                  <MenuItems className="absolute right-0 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none divide-y divide-gray-100 z-50">
                    <div className="px-4 py-3">
                      <p className="text-sm font-medium text-gray-900">
                        {user.displayName || "User"}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
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
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "flex px-4 py-2 text-sm items-center w-full"
                            )}
                          >
                            <FaUser className="mr-3 h-5 w-5 text-gray-400" />
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
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "flex px-4 py-2 text-sm items-center w-full"
                            )}
                          >
                            <FaCog className="mr-3 h-5 w-5 text-gray-400" />
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
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "flex px-4 py-2 text-sm items-center w-full"
                            )}
                          >
                            {isLoggingOut ? (
                              <>
                                <div className="mr-3 h-5 w-5 border-t-2 border-b-2 border-indigo-500 rounded-full animate-spin" />
                                Signing out...
                              </>
                            ) : (
                              <>
                                <FaSignOutAlt className="mr-3 h-5 w-5 text-gray-400" />
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
            ) : (
              <div className="ml-4">
                <Link
                  to="/login"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                >
                  Login
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex lg:hidden">
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-indigo-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-50 transition-colors"
            >
              <span className="sr-only">Open main menu</span>
              <FaBars className="block h-6 w-6" aria-hidden="true" />
            </button>
          </div>
        </div>

        {/* Patient Details */}
        {patientId && (loading || error || patient) && (
          <div className="bg-indigo-50 p-4 rounded-lg mb-4 mt-2 shadow-sm">
            {loading && (
              <div className="flex items-center space-x-2 text-blue-800">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
                <span className="text-sm font-medium">
                  Loading patient details...
                </span>
              </div>
            )}
            {error && (
              <div className="flex items-center space-x-2 text-red-800">
                <FaTimes className="h-5 w-5" aria-hidden="true" />
                <span className="text-sm font-medium">{error}</span>
              </div>
            )}
            {patient && !loading && !error && (
              <>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-indigo-800">
                    Current Patient
                  </h3>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                    Active
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-gray-600 font-medium">Name</p>
                    <p className="text-gray-900">{patient.name || "N/A"}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 font-medium">Age</p>
                    <p className="text-gray-900">{patient.age || "N/A"}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 font-medium">Gender</p>
                    <p className="text-gray-900">{patient.gender || "N/A"}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 font-medium">Contact</p>
                    <p className="text-gray-900">
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
        <div className="fixed inset-0 z-50 bg-black bg-opacity-25" />
        <DialogPanel className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
          <div className="flex items-center justify-between">
            <Link
              to="/"
              className="-m-1.5 p-1.5"
              onClick={() => setMobileMenuOpen(false)}
            >
              <img
                className="h-9 w-auto"
                src="/T-logo-removed.png"
                alt="Your Logo"
              />
            </Link>
            <button
              type="button"
              className="-m-2.5 rounded-md p-2.5 text-gray-700 hover:text-indigo-600 hover:bg-gray-100 transition-colors"
              onClick={() => setMobileMenuOpen(false)}
            >
              <span className="sr-only">Close menu</span>
              <FaTimes className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div className="mt-6 flow-root">
            <div className="-my-6 divide-y divide-gray-500/10">
              <div className="space-y-2 py-6">
                <Popover className="relative">
                  {({ open }) => (
                    <>
                      <PopoverButton
                        className={classNames(
                          open ? "text-indigo-600" : "text-gray-900",
                          "flex w-full items-center justify-between rounded-lg py-2 pl-3 pr-3.5 text-base font-semibold leading-7 hover:bg-gray-50 transition-colors"
                        )}
                      >
                        Services
                        <FaChevronDown
                          className={classNames(
                            open
                              ? "rotate-180 text-indigo-600"
                              : "text-gray-700",
                            "h-4 w-4 flex-none"
                          )}
                          aria-hidden="true"
                        />
                      </PopoverButton>
                      <PopoverPanel className="mt-2 space-y-2">
                        {products.map((item) => (
                          <Link
                            key={item.name}
                            to={item.href}
                            onClick={() => setMobileMenuOpen(false)}
                            className="block rounded-lg py-2 pl-6 pr-3 text-sm font-semibold leading-7 text-gray-900 hover:bg-gray-50 transition-colors"
                          >
                            <div className="flex items-center">
                              <item.icon
                                className="mr-3 h-5 w-5 text-indigo-600"
                                aria-hidden="true"
                              />
                              {item.name}
                            </div>
                          </Link>
                        ))}
                      </PopoverPanel>
                    </>
                  )}
                </Popover>

                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50 transition-colors"
                >
                  Home
                </Link>
                <Link
                  to="/about"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50 transition-colors"
                >
                  About
                </Link>
                <Link
                  to="/help"
                  onClick={() => setMobileMenuOpen(false)}
                  className="-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50 transition-colors"
                >
                  FAQ
                </Link>
              </div>
              <div className="py-6">
                {user ? (
                  <div className="space-y-4">
                    <div className="flex items-center px-4 py-3">
                      {user.photoURL ? (
                        <img
                          className="h-10 w-10 rounded-full"
                          src={user.photoURL}
                          alt="User profile"
                        />
                      ) : (
                        <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                          <span className="text-indigo-600 font-medium">
                            {user.email?.charAt(0).toUpperCase() || "U"}
                          </span>
                        </div>
                      )}
                      <div className="ml-3">
                        <p className="text-base font-medium text-gray-800">
                          {user.displayName || "User"}
                        </p>
                        <p className="text-sm font-medium text-gray-500">
                          {user.email}
                        </p>
                      </div>
                    </div>
                    <div className="border-t border-gray-200 pt-4">
                      <Link
                        to="/profile"
                        onClick={() => setMobileMenuOpen(false)}
                        className="flex items-center px-4 py-2 text-base font-medium text-gray-700 hover:bg-gray-100 rounded-md"
                      >
                        <FaUser className="mr-3 h-5 w-5 text-gray-400" />
                        Your Profile
                      </Link>
                      <button
                        onClick={() => {
                          handleLogout();
                          setMobileMenuOpen(false);
                        }}
                        disabled={isLoggingOut}
                        className="flex items-center px-4 py-2 text-base font-medium text-gray-700 hover:bg-gray-100 rounded-md w-full"
                      >
                        {isLoggingOut ? (
                          <>
                            <div className="mr-3 h-5 w-5 border-t-2 border-b-2 border-indigo-500 rounded-full animate-spin" />
                            Signing out...
                          </>
                        ) : (
                          <>
                            <FaSignOutAlt className="mr-3 h-5 w-5 text-gray-400" />
                            Sign out
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full flex justify-center items-center px-4 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Login
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="w-full flex justify-center items-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
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
