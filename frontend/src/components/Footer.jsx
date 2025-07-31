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
    <footer className="bg-gray-900 text-gray-300 pt-16 pb-8 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        {/* Logo and Top Section */}
        <div className="flex flex-col items-center mb-12">
          <Link to="/" className="mb-6">
            <img
              src="https://i.postimg.cc/wxJ7TKPg/clarity.png" // Replace with your logo path
              alt="ClarityDX Logo"
              className="h-36 w-auto"
            />
          </Link>
          <p className="text-center max-w-2xl mx-auto text-lg text-gray-400">
            Precise and reliable diagnostics tailored for every need
          </p>
        </div>

        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* About Section */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white mb-4">About Us</h3>
            <p className="text-gray-400">
              Delivering empathetic healthcare solutions powered by AI and ML to
              support medical professionals.
            </p>

            <address className="not-italic text-gray-400 mt-4">
              <p>Accra, Ghana</p>
            </address>
          </div>

          {/* Services */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white mb-4">Services</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/conditions" className="hover:text-white transition">
                  Conditions
                </Link>
              </li>
              <li>
                <Link
                  to="/appointments"
                  className="hover:text-white transition"
                >
                  Make Appointment
                </Link>
              </li>
              <li>
                <Link to="/doctors" className="hover:text-white transition">
                  Our Doctors
                </Link>
              </li>
              <li>
                <Link to="/articles" className="hover:text-white transition">
                  Health Articles
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-white transition">
                  Contact Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/privacy" className="hover:text-white transition">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="hover:text-white transition">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/faq" className="hover:text-white transition">
                  FAQs
                </Link>
              </li>
              <li>
                <Link to="/careers" className="hover:text-white transition">
                  Careers
                </Link>
              </li>
              <li>
                <Link
                  to="/testimonials"
                  className="hover:text-white transition"
                >
                  Patient Stories
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact & Social */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-white mb-4">Contact Us</h3>
            <div className="space-y-2 text-gray-400">
              <p>Office: 00091997052300</p>
              <p>Mobile: 000 2222 12345</p>
              <p>Email: info@claritydx.com</p>
            </div>

            <div className="mt-6">
              <h4 className="text-lg font-semibold text-white mb-3">
                Follow Us
              </h4>
              <div className="flex space-x-4">
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaFacebook size={20} />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaTwitter size={20} />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaInstagram size={20} />
                </a>
                <a
                  href="#"
                  className="text-gray-400 hover:text-white transition"
                >
                  <FaLinkedin size={20} />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Copyright and Attribution */}
        <div className="border-t border-gray-800 pt-6 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-500 text-sm mb-4 md:mb-0">
            &copy; {new Date().getFullYear()} ClarityDX. All rights reserved.
          </p>
          <p className="text-gray-500 text-sm flex items-center">
            Made with <FaHeart className="mx-1 text-red-400" /> by YBoye
            Emmanuel Tete
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
