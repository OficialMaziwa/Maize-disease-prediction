import tensorflow as tf
import numpy as np
import json
import os
from tensorflow.keras.preprocessing import image

class MaizeDiseaseModel:
    def __init__(self):
        self.model = None
        self.class_names = None
        self.idx_to_class = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and class names"""
        # Try different possible paths
        model_paths = [
            'maize_disease_model.h5',
            'app/models/maize_disease_model.h5',
            '../maize_disease_model.h5'
        ]
        
        class_paths = [
            'class_names.json',
            'app/models/class_names.json',
            '../class_names.json'
        ]
        
        # Load model
        for path in model_paths:
            if os.path.exists(path):
                try:
                    self.model = tf.keras.models.load_model(path)
                    print(f"✅ Model loaded from {path}")
                    break
                except Exception as e:
                    print(f"Error loading from {path}: {e}")
        
        if self.model is None:
            print("❌ Could not load model from any path")
            return False
        
        # Load class names
        for path in class_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        self.class_names = json.load(f)
                    print(f"✅ Class names loaded from {path}")
                    break
                except Exception as e:
                    print(f"Error loading classes from {path}: {e}")
        
        if self.class_names is None:
            # Default class names if file not found
            self.class_names = {
                'Blight': 0,
                'Common_Rust': 1,
                'Gray_Leaf_Spot': 2,
                'Healthy': 3
            }
            print("📋 Using default class names")
        
        # Create reverse mapping
        self.idx_to_class = {v: k for k, v in self.class_names.items()}
        return True
    
    def predict(self, img_path):
        """Predict disease from image path"""
        if self.model is None:
            return None, 0, None
        
        # Load and preprocess image
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        
        # Make prediction
        predictions = self.model.predict(img_array, verbose=0)
        predicted_idx = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0]) * 100)
        
        predicted_class = self.idx_to_class.get(predicted_idx, "Unknown")
        
        # Get all probabilities
        all_probs = {
            self.idx_to_class.get(i, f"Class_{i}"): float(predictions[0][i] * 100)
            for i in range(len(self.class_names))
        }
        
        return predicted_class, confidence, all_probs
    
    def get_recommendation(self, disease):
        """Get treatment recommendation based on disease"""
        recommendations = {
            'Healthy': '✅ Your maize plant appears healthy! Continue good farming practices including proper watering, fertilization, and regular monitoring.',
            
            'Blight': '🚨 Turcicum Leaf Blight (Northern Corn Leaf Blight) detected.\n\n'
                      '📋 RECOMMENDATIONS:\n'
                      '• Apply fungicides containing azoxystrobin, pyraclostrobin, or propiconazole\n'
                      '• Remove and destroy infected leaves\n'
                      '• Practice crop rotation (2-3 years) with non-host crops\n'
                      '• Use resistant hybrid varieties\n'
                      '• Ensure proper plant spacing for air circulation\n'
                      '• Apply nitrogen fertilizer at recommended rates',
            
            'Common_Rust': '🚨 Common Rust detected.\n\n'
                          '📋 RECOMMENDATIONS:\n'
                          '• Plant resistant varieties in future seasons\n'
                          '• Apply fungicides like mancozeb or azoxystrobin if severe\n'
                          '• Maintain proper plant nutrition\n'
                          '• Remove volunteer corn plants that can harbor the disease\n'
                          '• Monitor fields regularly, especially in humid conditions',
            
            'Gray_Leaf_Spot': '🚨 Gray Leaf Spot detected.\n\n'
                            '📋 RECOMMENDATIONS:\n'
                            '• Apply fungicides (strobilurins, triazoles, or combinations)\n'
                            '• Improve air circulation through proper spacing\n'
                            '• Avoid overhead irrigation\n'
                            '• Practice crop rotation with soybeans or other non-host crops\n'
                            '• Use resistant hybrids\n'
                            '• Remove crop residue after harvest'
        }
        
        return recommendations.get(disease, 'Please consult with a local agricultural extension officer for treatment advice.')

# Create a singleton instance
model_instance = MaizeDiseaseModel()