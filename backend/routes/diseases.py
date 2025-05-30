from flask import Blueprint, request, jsonify
from services.diagnosis_service import diagnose_symptoms
from services.image_processing_service import process_image

disease_bp = Blueprint("diseases", __name__)

@disease_bp.route("/diagnose", methods=["POST"])
def diagnose():
    try:
        data = request.json  # Get JSON input from frontend

        if not data and "image" not in request.files:
            return jsonify({"error": "Invalid request. Provide symptoms or an image."}), 400

        diagnosis = None

        if data and "symptoms" in data and isinstance(data["symptoms"], list) and data["symptoms"]:
            diagnosis = diagnose_symptoms(data["symptoms"])
        elif "image" in request.files:
            image = request.files["image"]
            diagnosis = process_image(image)
        else:
            return jsonify({"error": "Invalid input format. Provide valid symptoms or an image."}), 400

        return jsonify({"diagnosis": diagnosis})

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
