# app/routes/disease.py
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
import base64
import io
from PIL import Image

# Create the blueprint
disease = Blueprint("disease", __name__)


@disease.route("/detect", methods=["GET", "POST"])
@login_required
def detect():
    if request.method == "POST":
        print("=" * 50)
        print("Received POST request to /disease/detect")

        if "image" not in request.files:
            print("No image in request")
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["image"]

        if file.filename == "":
            print("Empty filename")
            return jsonify({"error": "No image selected"}), 400

        try:
            # Read and process image
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))

            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Save to session
            session["image_data"] = base64.b64encode(img_bytes).decode("utf-8")

            # Mock result (replace with your actual model)
            result = {
                "disease": "Northern Leaf Blight",
                "confidence": 0.95,
                "severity": "Moderate",
                "treatment": "Apply fungicide (Azoxystrobin) and remove infected leaves",
                "prevention": "Crop rotation, resistant varieties, proper spacing",
            }

            session["prediction_result"] = result

            # Return JSON for AJAX requests
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": True, "redirect": "/disease/result"})

            return render_template("disease/result.html", result=result)

        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500

    return render_template("disease/detect.html")


@disease.route("/result")
@login_required
def result():
    result = session.get("prediction_result")
    image_data = session.get("image_data")

    if not result:
        return redirect("/disease/detect")

    return render_template("disease/result.html", result=result, image_data=image_data)


@disease.route("/test")
@login_required
def test():
    return render_template("disease/test_upload.html")
