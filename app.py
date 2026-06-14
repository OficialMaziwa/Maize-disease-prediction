from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import json
from werkzeug.utils import secure_filename
from PIL import Image

# Import language manager
from app.language_manager import lang_manager

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static",
)
app.secret_key = os.urandom(24)

# Configuration
UPLOAD_FOLDER = "app/static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "JPG", "JPEG", "PNG"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the trained model
MODEL_PATH = "maize_disease_model.h5"
CLASS_NAMES_PATH = "class_names.json"

# Try loading from app/models if not in root
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "app/models/maize_disease_model.h5"
    CLASS_NAMES_PATH = "app/models/class_names.json"

print("=" * 50)
print("🌽 MAIZE DISEASE DETECTION API")
print("=" * 50)
print(f"Current directory: {os.getcwd()}")
print(f"Template folder: {app.template_folder}")
print(f"Model path: {MODEL_PATH}")
print(f"Class names path: {CLASS_NAMES_PATH}")

# Load model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# Load class names - FIXED for your JSON structure
try:
    with open(CLASS_NAMES_PATH, "r") as f:
        class_names_data = json.load(f)

    print(f"📋 Raw class names type: {type(class_names_data)}")

    # Extract the actual class names list
    if isinstance(class_names_data, dict):
        if "class_names" in class_names_data and isinstance(
            class_names_data["class_names"], list
        ):
            class_list = class_names_data["class_names"]
            print(f"✅ Found 'class_names' key with {len(class_list)} classes")
        elif "display_names" in class_names_data and isinstance(
            class_names_data["display_names"], dict
        ):
            class_list = list(class_names_data["display_names"].keys())
            print(f"✅ Found 'display_names' key with {len(class_list)} classes")
        elif "folder_to_display" in class_names_data and isinstance(
            class_names_data["folder_to_display"], dict
        ):
            class_list = list(class_names_data["folder_to_display"].values())
            print(f"✅ Found 'folder_to_display' key with {len(class_list)} classes")
        else:
            # Try to find any list in the dictionary
            class_list = None
            for key, value in class_names_data.items():
                if isinstance(value, list):
                    class_list = value
                    print(
                        f"✅ Found list under '{key}' key with {len(class_list)} classes"
                    )
                    break

            if class_list is None:
                # Use dictionary keys as class names
                class_list = list(class_names_data.keys())
                print(
                    f"✅ Using dictionary keys as class names: {len(class_list)} classes"
                )
    elif isinstance(class_names_data, list):
        class_list = class_names_data
        print(f"✅ JSON is a list with {len(class_list)} classes")
    else:
        raise ValueError(f"Unexpected JSON format: {type(class_names_data)}")

    # Create proper class_names mapping
    class_names = {class_name: idx for idx, class_name in enumerate(class_list)}
    print(f"✅ Class names loaded: {list(class_names.keys())}")

except Exception as e:
    print(f"❌ Error loading class names: {e}")
    print("📋 Using default class names")
    class_names = {"Blight": 0, "Common_Rust": 1, "Gray_Leaf_Spot": 2, "Healthy": 3}
    print(f"✅ Default class names: {list(class_names.keys())}")

# Reverse mapping for prediction
idx_to_class = {v: k for k, v in class_names.items()}
num_classes = len(class_names)

print(f"\n📊 Class mapping created successfully:")
for idx, name in idx_to_class.items():
    print(f"   {idx} -> {name}")


# ============ LINK LANGUAGE MANAGER - COMPLETE ============
@app.context_processor
def utility_processor():
    """Make language manager available to all templates"""

    def get_text(key, lang=None):
        """Get translation from language manager.
        Usage:
        - {{ t('welcome') }} - uses session language
        - {{ t('welcome', 'en') }} - forces English
        """
        # If lang is not provided, get from session
        if lang is None:
            lang = session.get("language", "en")

        # Use your language manager to get translation
        return lang_manager.get_text(key, lang)

    return dict(t=get_text, current_lang=session.get("language", "en"), request=request)


# Route to change language
@app.route("/change-language/<lang>")
def change_language(lang):
    """Change application language"""
    if lang in ["en", "sw"]:
        session["language"] = lang
    return redirect(request.referrer or url_for("home"))


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def predict_image(image_path):
    """Predict disease from image path"""
    if model is None:
        return None, 0, None

    # Load and preprocess image
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize

    # Predict
    predictions = model.predict(img_array, verbose=0)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(np.max(predictions[0]) * 100)

    # Get class name
    predicted_class = idx_to_class.get(predicted_class_idx, "Unknown")

    # Get all class probabilities
    all_probabilities = {
        idx_to_class[i]: float(predictions[0][i] * 100) for i in range(num_classes)
    }

    return predicted_class, confidence, all_probabilities


@app.route("/")
def home():
    """Home page"""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """Handle image upload and prediction"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return (
            jsonify(
                {
                    "error": f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
                }
            ),
            400,
        )

    try:
        # Save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Make prediction
        predicted_class, confidence, all_probabilities = predict_image(filepath)

        if predicted_class is None:
            return jsonify({"error": "Model not loaded properly"}), 500

        # Prepare response
        response = {
            "success": True,
            "prediction": predicted_class,
            "confidence": round(confidence, 2),
            "all_probabilities": all_probabilities,
            "image_url": f"/static/uploads/{filename}",
        }

        # Add recommendation based on prediction
        if predicted_class == "Healthy":
            response["recommendation"] = (
                "✅ Your maize plant appears healthy! Continue good farming practices."
            )
        elif predicted_class == "Blight":
            response["recommendation"] = (
                "🚨 Turcicum Leaf Blight detected. Recommended: Apply fungicides containing azoxystrobin or pyraclostrobin, remove infected leaves, and practice crop rotation."
            )
        elif predicted_class == "Common_Rust":
            response["recommendation"] = (
                "🚨 Common Rust detected. Recommended: Use resistant varieties, apply fungicides if severe, and maintain proper plant spacing."
            )
        elif predicted_class == "Gray_Leaf_Spot":
            response["recommendation"] = (
                "🚨 Gray Leaf Spot detected. Recommended: Improve air circulation, avoid overhead irrigation, apply fungicides like strobilurins or triazoles."
            )
        else:
            response["recommendation"] = (
                "Please consult with a local agricultural extension officer for treatment advice."
            )

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": model is not None,
            "classes_available": list(class_names.keys()),
            "num_classes": num_classes,
        }
    )


@app.route("/debug/info")
def debug_info():
    """Debug information"""
    templates = []
    if os.path.exists(app.template_folder):
        templates = os.listdir(app.template_folder)

    return jsonify(
        {
            "current_directory": os.getcwd(),
            "template_folder": app.template_folder,
            "templates_found": templates,
            "model_loaded": model is not None,
            "classes": list(class_names.keys()),
        }
    )


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🚀 Starting Flask Server...")
    print("📱 Access the web interface at: http://127.0.0.1:5000")
    print("🔍 Health check at: http://127.0.0.1:5000/health")
    print("🔍 Debug info at: http://127.0.0.1:5000/debug/info")
    print("=" * 50 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
