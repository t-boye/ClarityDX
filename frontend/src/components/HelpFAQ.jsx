import React, { useState } from "react";

const HelpFAQ = () => {
  const [activeIndex, setActiveIndex] = useState(null);

  const faqs = [
    {
      question: "How does the symptom checker work?",
      answer:
        "Our symptom checker analyzes the symptoms you report using validated medical algorithms to assess the likelihood of malaria. Simply enter your symptoms and their duration to receive an initial assessment.",
    },
    {
      question: "How accurate is the diagnosis?",
      answer:
        "While our system uses evidence-based guidelines, it's not a substitute for professional medical diagnosis. Accuracy depends on the symptoms reported. We recommend consulting a healthcare provider for confirmation.",
    },
    {
      question: "Where can I get treatment?",
      answer:
        "Malaria treatment is available at most hospitals, clinics, and health centers. Our system can help you locate the nearest treatment facility based on your location.",
    },
  ];

  const toggleFAQ = (index) => {
    setActiveIndex(activeIndex === index ? null : index);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        Help & Frequently Asked Questions
      </h2>
      <p className="text-gray-600 mb-8 text-center">
        Find answers to common questions about Malaria and this system.
      </p>

      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg overflow-hidden transition-all duration-200"
          >
            <button
              className="w-full px-5 py-4 text-left bg-gray-50 hover:bg-gray-100 flex justify-between items-center"
              onClick={() => toggleFAQ(index)}
            >
              <span className="font-medium text-gray-800">{faq.question}</span>
              <svg
                className={`w-5 h-5 text-gray-500 transform transition-transform ${
                  activeIndex === index ? "rotate-180" : ""
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {activeIndex === index && (
              <div className="px-5 py-4 bg-white text-gray-600">
                <p>{faq.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
        <h3 className="font-medium text-blue-800 mb-2">Need more help?</h3>
        <p className="text-blue-600">
          Contact our support team at support@malariahelp.org or call +1 (800)
          555-HELP
        </p>
      </div>
    </div>
  );
};

export default HelpFAQ;
