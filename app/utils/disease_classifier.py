
import tensorflow as tf
import numpy as np
from PIL import Image
import os


class DiseaseClassifier:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join("app", "models", "maize_disease_model.h5")

        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.model = None
            print(f"Warning: Model not found at {model_path}")

    def predict(self, image_path):
        return {
            "disease": "Northern Leaf Blight",
            "confidence": 0.95,
            "treatment": "Apply fungicide and remove infected leaves",
        }
