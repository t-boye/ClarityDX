def diagnose_symptoms(symptoms):
    rules = {
        "malaria": ["fever", "chills", "sweating", "headache", "fatigue"],
        "typhoid": ["fever", "abdominal pain", "headache", "diarrhea"],
        "dengue": ["fever", "rash", "joint pain", "muscle pain"]
    }

    for disease, disease_symptoms in rules.items():
        if all(symptom in disease_symptoms for symptom in symptoms):
            return f"Possible {disease} detected. Consult a doctor."

    return "No strong match found. Further tests may be needed."
