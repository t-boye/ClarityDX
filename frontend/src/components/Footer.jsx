import React from "react";
import { Link } from "react-router-dom";
import {
  FaFacebook,
  FaTwitter,
  FaInstagram,
  FaLinkedin,
  FaHeart,
} from "react-icons/fa";

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 pt-10 pb-6 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        {/* Logo and Top Section */}
        <div className="flex flex-col items-center mb-8">
          <Link to="/" className="mb-4">
            <img
              src="https://i.postimg.cc/wxJ7TKPg/clarity.png"
              alt="ClarityDX Logo"
              className="h-20 w-auto"
            />
          </Link>
          <p className="text-center max-w-xl mx-auto text-sm text-gray-400">
            Precise and reliable diagnostics tailored for every need
          </p>
        </div>

        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {/* About Section */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-white mb-3">About Us</h3>
            <p className="text-sm text-gray-400">
              Delivering empathetic healthcare solutions powered by AI and ML to
              support medical professionals.
            </p>

            <address className="not-italic text-sm text-gray-400 mt-3">
              <p>Accra, Ghana</p>
            </address>
          </div>

          {/* Services */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-white mb-3">Services</h3>
            <ul className="space-y-1.5">
              {/* <li>
                <Link
                  to="/conditions"
                  className="hover:text-white transition text-sm"
                >
                  Conditions
                </Link>
              </li>
              <li>
                <Link
                  to="/appointments"
                  className="hover:text-white transition text-sm"
                >
                  Make Appointment
                </Link>
              </li> */}
              <li>
                <Link
                  to="/doctors"
                  className="hover:text-white transition text-sm"
                >
                  Our Doctors
                </Link>
              </li>
              <li>
                <Link
                  to="/articles"
                  className="hover:text-white transition text-sm"
                >
                  Health Articles
                </Link>
              </li>
              <li>
                <Link
                  to="/contact"
                  className="hover:text-white transition text-sm"
                >
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Quick Links */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-white mb-3">Quick Links</h3>
            <ul className="space-y-1.5">
              <li>
                <Link
                  to="/privacy"
                  className="hover:text-white transition text-sm"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  to="/terms"
                  className="hover:text-white transition text-sm"
                >
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/faq" className="hover:text-white transition text-sm">
                  FAQs
                </Link>
              </li>
              {/* <li>
                <Link
                  to="/careers"
                  className="hover:text-white transition text-sm"
                >
                  Careers
                </Link>
              </li>
              <li>
                <Link
                  to="/testimonials"
                  className="hover:text-white transition text-sm"
                >
                  Patient Stories
                </Link>
              </li> */}
            </ul>
          </div>

          {/* Contact & Social */}
          <div className="space-y-3">
            <h3 className="text-lg font-bold text-white mb-3">Contact Us</h3>
            <div className="space-y-1.5 text-sm text-gray-400">
              <p>Office: 00091997052300</p>
              <p>Mobile: 000 2222 12345</p>
              <p>Email: info@claritydx.com</p>
            </div>

            <div className="mt-4">
              <h4 className="text-base font-semibold text-white mb-2">
                Follow Us
              </h4>
              <div className="flex space-x-3">
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaFacebook size={16} />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaTwitter size={16} />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaInstagram size={16} />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaLinkedin size={16} />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Copyright and Attribution */}
        <div className="border-t border-gray-800 pt-4 flex flex-col md:flex-row justify-between items-center">
          <p className="text-xs text-gray-500 mb-3 md:mb-0">
            &copy; {new Date().getFullYear()} ClarityDX. All rights reserved.
          </p>
          <p className="text-xs text-gray-500 flex items-center">
            Made with <FaHeart className="mx-1 text-red-400" size={12} /> by
            Boye Emmanuel Tete
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
