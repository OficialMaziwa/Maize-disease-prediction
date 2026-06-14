import os
import sys
import json
import numpy as np
from PIL import Image
import io
import logging

# Set TensorFlow environment variables
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

logger = logging.getLogger(__name__)


class MaizeDiseaseDetector:
    def __init__(self, model_path=None):
        self.model = None
        self.class_names = None
        self.idx_to_class = None

        # Import TensorFlow
        try:
            import tensorflow as tf
            from tensorflow import keras

            self.tf = tf
            self.keras = keras
            print("✅ TensorFlow imported successfully")
        except ImportError as e:
            print(f"❌ TensorFlow import error: {e}")
            self.tf = None
            self.keras = None

        # Find and load model
        if model_path is None:
            possible_paths = [
                "maize_disease_model.h5",
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "maize_disease_model.h5",
                ),
                os.path.join(os.getcwd(), "maize_disease_model.h5"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    print(f"✅ Found model: {model_path}")
                    break

        # Load model
        if model_path and os.path.exists(model_path) and self.keras:
            try:
                self.model = self.keras.models.load_model(model_path)
                print(f"✅ Model loaded: {model_path}")
            except Exception as e:
                print(f"❌ Model load error: {e}")
                self.model = None

        # Load class names
        class_paths = [
            "class_names.json",
            os.path.join(os.getcwd(), "class_names.json"),
        ]
        for path in class_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        print(f"✅ Loaded class data from {path}")

                        if isinstance(data, dict) and "class_names" in data:
                            self.class_names = data["class_names"]
                        elif isinstance(data, list):
                            self.class_names = data
                        else:
                            self.class_names = list(data.keys())

                        print(f"✅ Class names: {self.class_names}")
                        self.idx_to_class = {
                            i: name for i, name in enumerate(self.class_names)
                        }
                        break
                except Exception as e:
                    print(f"Error loading classes: {e}")

        if self.class_names is None:
            self.class_names = ["Blight", "Common_Rust", "Gray_Leaf_Spot", "Healthy"]
            self.idx_to_class = {
                0: "Blight",
                1: "Common_Rust",
                2: "Gray_Leaf_Spot",
                3: "Healthy",
            }
            print(f"📋 Default class names: {self.class_names}")

    def predict_from_bytes(self, image_bytes):
        """Predict disease from image bytes"""
        print("=" * 50)
        print("🔍 PREDICTION STARTED")
        print("=" * 50)

        if self.model is None:
            print("⚠️ Model not loaded, returning Healthy")
            return "Healthy", 85.0

        try:
            # Load and preprocess image
            img = Image.open(io.BytesIO(image_bytes))
            print(f"📸 Original image: {img.size}, {img.mode}")

            # Resize to 224x224
            img = img.resize((224, 224))
            print(f"📸 Resized image: {img.size}")

            # Convert to RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
                print(f"📸 Converted to RGB")

            # Convert to array and normalize
            img_array = np.array(img).astype(np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            print(f"📊 Image array shape: {img_array.shape}")

            # Predict
            predictions = self.model.predict(img_array, verbose=0)[0]
            print(f"📊 Raw predictions: {predictions}")

            # Print all probabilities
            print("\n📊 Prediction probabilities:")
            for i, name in enumerate(self.class_names):
                print(f"   {name}: {predictions[i]*100:.1f}%")

            # Get predicted class
            predicted_idx = np.argmax(predictions)
            confidence = float(predictions[predicted_idx] * 100)
            disease_name = self.idx_to_class.get(predicted_idx, "Unknown")

            print(f"\n🎯 FINAL RESULT: {disease_name} ({confidence:.1f}%)")
            print("=" * 50)
            return disease_name, confidence

        except Exception as e:
            print(f"❌ Prediction error: {e}")
            import traceback

            traceback.print_exc()
            return "Healthy", 85.0


# Create instance
detector = MaizeDiseaseDetector()
