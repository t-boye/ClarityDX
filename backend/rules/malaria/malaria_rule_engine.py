import logging
from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(level=logging.INFO)


class MalariaInputData(BaseModel):
    """
    Represents the input data for malaria risk assessment.

    Attributes:
        age: The patient's age (non-negative integer).
        gender: The patient's gender ("male" or "female").
        travelHistory: Recent travel to malaria-prone areas ("yes", "no").
        mosquitoExposure: Frequent mosquito bites ("yes", "no", "maybe").
        symptoms: A list of symptoms experienced by the patient.
    """

    age: Optional[int] = Field(ge=0, default=None)  # Age must be non-negative
    gender: Optional[Literal["male", "female"]] = Field(default=None)
    travelHistory: Optional[Literal["yes", "no"]] = Field(default=None)
    mosquitoExposure: Optional[Literal["yes", "no", "maybe"]] = Field(default=None)
    symptoms: Optional[List[str]] = Field(default_factory=list)


def assess_malaria_risk(data: MalariaInputData) -> dict:
    """
    Assesses malaria risk based on user-provided data.

    Args:
        data: An instance of MalariaInputData containing user input.

    Returns:
        A dictionary with the risk assessment, recommendations, and additional information.
    """

    logging.info("Starting malaria risk assessment.")
    logging.debug(f"Input data: {data.model_dump()}")  # Use model_dump() for logging

    risk_level = "low"  # Default risk level
    recommendation = "Malaria is unlikely. Monitor symptoms."
    additional_info = []  # List to store additional relevant information

    # Expand Symptoms List
    common_symptoms = ["fever", "chills", "headache", "fatigue", "nausea", "vomiting", "muscle-pain"]
    severe_symptoms = ["severe-anemia", "seizures", "confusion"]
    other_symptoms = ["abdominal-pain", "cough"]

    # --- Risk Assessment Rules ---

    # Rule 1: High risk - Travel + Exposure + Key Symptoms
    if (
        data.travelHistory == "yes"
        and data.mosquitoExposure in ("yes", "maybe")
        and any(s in data.symptoms for s in ["fever", "chills"])
    ):
        risk_level = "high"
        recommendation = (
            "High risk of malaria. Seek immediate medical attention for testing."
        )
        additional_info.append("Recent travel and mosquito exposure are significant risk factors.")

    # Rule 2: Moderate risk - Travel OR Exposure + Some Symptoms
    elif (
        data.travelHistory == "yes" or data.mosquitoExposure in ("yes", "maybe")
    ) and any(s in data.symptoms for s in common_symptoms):
        risk_level = "moderate"
        recommendation = "Moderate risk of malaria. Consult a doctor for evaluation."
        additional_info.append("Travel or mosquito exposure increases the likelihood.")

    # Rule 3: High risk - Severe symptoms
    if any(s in data.symptoms for s in severe_symptoms):
        risk_level = "high"
        recommendation = "Emergency medical attention is required."
        additional_info.append("Severe symptoms indicate a serious condition.")

    # Rule 4: Age Groups
    if data.age is not None:
        if data.age < 5:
            if risk_level != "high":
                risk_level = "high"
                recommendation = "Young children are at high risk. Seek immediate medical attention."
                additional_info.append("Children under 5 are highly vulnerable to severe malaria.")
        elif data.age > 60:
            if risk_level != "high":
                risk_level = "moderate"
                recommendation = "Older adults may experience more severe malaria. Consider testing."
                additional_info.append("Older adults are at increased risk of complications.")

    # Rule 5: Gender Considerations (Example - further research needed)
    if data.gender == "male" and risk_level == "low" and "fever" in data.symptoms:
        risk_level = "moderate"
        recommendation = "Male gender with fever warrants further investigation."
        additional_info.append("Some studies suggest gender may influence malaria risk.")

    # Rule 6: No travel or exposure, few symptoms
    if data.travelHistory == "no" and data.mosquitoExposure == "no" and len(data.symptoms) < 2:
        recommendation = "Malaria is unlikely. Consider other possible causes of your symptoms."
        additional_info.append("Low likelihood of malaria without travel or exposure.")

    logging.info(f"Risk level: {risk_level}")
    logging.info(f"Recommendation: {recommendation}")
    logging.debug(f"Additional info: {additional_info}")

    return {
        "risk_level": risk_level,
        "recommendation": recommendation,
        "additional_info": additional_info,
    }


if __name__ == "__main__":
    # Example Usage (for testing)
    try:
        data1 = MalariaInputData(
            age=30,
            gender="male",
            travelHistory="yes",
            mosquitoExposure="yes",
            symptoms=["fever", "chills", "headache"],
        )
        result1 = assess_malaria_risk(data1)
        print(f"Test Case 1: {result1}")

        data2 = MalariaInputData(
            age=4, gender="female", symptoms=["fever", "fatigue", "severe-anemia"]
        )
        result2 = assess_malaria_risk(data2)
        print(f"Test Case 2: {result2}")

        data3 = MalariaInputData(
            age=70, gender="male", symptoms=["seizures", "confusion"]
        )
        result3 = assess_malaria_risk(data3)
        print(f"Test Case 3: {result3}")

        data4 = MalariaInputData(
            age=25, gender="female", travelHistory="no", mosquitoExposure="no", symptoms=["headache"]
        )
        result4 = assess_malaria_risk(data4)
        print(f"Test Case 4: {result4}")

    except ValidationError as e:
        print(f"Validation Error: {e.errors()}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")