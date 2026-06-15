import os
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import requests

MODEL_URL = "https://drive.google.com/uc?id=1LeYuYnY6tAr1qR7Jke7qOPkLt8Ue2yrY"
MODEL_PATH = "app/models/maize_disease_model.h5"

print("=== KUHAMISHA MFANO ===")
# 1. Pakua mfano ikiwa haipo
if not os.path.exists(MODEL_PATH):
    print(f"📥 Inapakua mfano kutoka: {MODEL_URL}")
    os.makedirs("app/models", exist_ok=True)
    # Tumia requests kwa sababu ni rahisi zaidi kuliko gdown
    response = requests.get(MODEL_URL, allow_redirects=True)
    with open(MODEL_PATH, "wb") as f:
        f.write(response.content)
    print("✅ Mfano umepakuliwa")

# 2. Jaribu kupakia mfano
print("🔄 Inapakia mfano...")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Mfano umepakiwa kikamilifu!")
    print(f"📊 Umbo la pembejeo (input shape): {model.input_shape}")
    print(f"📊 Umbo la matokeo (output shape): {model.output_shape}")
    
    # 3. Jaribu kufanya utabiri wa majaribio kwa picha bandia
    test_input = np.random.rand(1, 224, 224, 3)  # Picha bandia
    test_output = model.predict(test_input, verbose=0)
    print(f"🧪 Utabiri wa majaribio: {test_output[0]}")
    print("=== MFANO UNAFANYA KAZI ===")
except Exception as e:
    print(f"❌ Hitilafu wakati wa kupakia mfano: {e}")
