import React from "react";
import { Link } from "react-router-dom";
import { FaGithub, FaLinkedin, FaTwitter, FaEnvelope } from "react-icons/fa";
import { IoMdHeart } from "react-icons/io";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const quickLinks = [
    { name: "Home", path: "/" },
    { name: "About", path: "/about" },
    { name: "Services", path: "/services" },
    { name: "Contact", path: "/contact" },
    { name: "Privacy Policy", path: "/privacy" },
    { name: "Terms of Service", path: "/terms" },
  ];

  const socialLinks = [
    {
      name: "GitHub",
      url: "https://github.com/t-boye",
      icon: <FaGithub className="h-5 w-5" />,
    },
    {
      name: "LinkedIn",
      url: "https://www.linkedin.com/in/tboyeofficial",
      icon: <FaLinkedin className="h-5 w-5" />,
    },
    // {
    //   name: "Twitter",
    //   url: "https://twitter.com/yourhandle",
    //   icon: <FaTwitter className="h-5 w-5" />,
    // },
    {
      name: "Email",
      url: "mailto:emmanuelboye1957@gmail.com",
      icon: <FaEnvelope className="h-5 w-5" />,
    },
  ];

  return (
    <footer className="bg-gray-800 text-gray-300">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8">
          {/* About Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">
              Expert Diagnosis System
            </h3>
            <p className="text-sm">
              AI-powered diagnostic tools for accurate and early disease
              detection.
            </p>
            <div className="flex space-x-4">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white transition-colors"
                  aria-label={social.name}
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Quick Links</h3>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.path}
                    className="text-sm hover:text-white transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Our Services</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  to="/malaria-diagnosis"
                  className="text-sm hover:text-white transition-colors"
                >
                  Malaria Diagnosis
                </Link>
              </li>
              <li>
                <Link
                  to="/hepatitis-diagnosis"
                  className="text-sm hover:text-white transition-colors"
                >
                  Hepatitis C Diagnosis
                </Link>
              </li>
              <li>
                <Link
                  to="/heart-disease-diagnosis"
                  className="text-sm hover:text-white transition-colors"
                >
                  Heart Disease Diagnosis
                </Link>
              </li>
              <li>
                <Link
                  to="/kidney-disease-diagnosis"
                  className="text-sm hover:text-white transition-colors"
                >
                  Kidney Disease Diagnosis
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Contact Us</h3>
            <address className="not-italic text-sm space-y-2">
              <p>8910 Medical Drive</p>
              <p>Accra - Ghana</p>
              <p>
                <a
                  href="tel:+1234567890"
                  className="hover:text-white transition-colors"
                >
                  +233 (0) 59-350-1488
                </a>
              </p>
              <p>
                <a
                  href="mailto:support@expertsystem.com"
                  className="hover:text-white transition-colors"
                >
                  support@expertsystem.com
                </a>
              </p>
            </address>
          </div>
        </div>

        {/* Copyright Section */}
        <div className="mt-12 pt-8 border-t border-gray-700 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm flex items-center">
            Made with <IoMdHeart className="mx-1 text-red-400" /> by Emmanuel
            Tete Boye
          </p>
          <p className="text-sm mt-4 md:mt-0">
            &copy; {currentYear} Expert System in Diagnosis. All rights
            reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
