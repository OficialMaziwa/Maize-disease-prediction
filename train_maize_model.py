"""
Maize Disease Detection Model Training Script
Using TensorFlow/Keras for training a CNN model
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from pathlib import Path
import shutil
import random

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

# Configuration
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 50

# Path to your dataset
DATASET_PATH = r"C:\Users\Official Maziwa\maize-disease-prediction\maize-disease-detection\dataset\training"

# Map your folder names to display names
FOLDER_TO_DISPLAY = {
    "Blight": "Turcicum Leaf Blight",
    "Common_Rust": "Common Rust",
    "Gray_Leaf_Spot": "Gray Leaf Spot",
    "Healthy": "Healthy",
}


# ============================================
# FUNCTION: CREATE TEST SET FROM TRAINING DATA
# ============================================
def create_test_set(train_path, test_path, test_size=0.15, min_images_per_class=20):
    """
    Create a test set by copying random images from training to test folder

    Args:
        train_path: Path to training folder
        test_path: Path to test folder (will be created)
        test_size: Proportion of images to copy to test (0.15 = 15%)
        min_images_per_class: Minimum images to keep in training after copying
    """
    print("\n" + "=" * 60)
    print("📁 CREATING TEST SET")
    print("=" * 60)

    # Create test directory
    os.makedirs(test_path, exist_ok=True)

    # Get all class folders
    class_folders = [
        d
        for d in os.listdir(train_path)
        if os.path.isdir(os.path.join(train_path, d)) and d not in ["__pycache__"]
    ]

    test_stats = {}
    total_test_images = 0

    for class_name in class_folders:
        source_dir = os.path.join(train_path, class_name)
        target_dir = os.path.join(test_path, class_name)

        # Create class subdirectory in test
        os.makedirs(target_dir, exist_ok=True)

        # Get all image files
        images = [
            f
            for f in os.listdir(source_dir)
            if f.endswith((".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"))
        ]

        # Calculate how many images to copy to test
        n_test = max(1, int(len(images) * test_size))

        # Ensure we don't take too many (leave at least min_images_per_class in training)
        n_test = min(n_test, len(images) - min_images_per_class)
        n_test = max(1, n_test)

        # Randomly select images for test set
        random.seed(42)  # For reproducibility
        test_images = random.sample(images, n_test)

        # Copy images to test folder
        for img in test_images:
            src = os.path.join(source_dir, img)
            dst = os.path.join(target_dir, img)
            shutil.copy2(src, dst)

        test_stats[class_name] = {
            "total": len(images),
            "test": n_test,
            "remaining": len(images) - n_test,
        }
        total_test_images += n_test

        print(
            f"   {class_name}: {n_test} images copied to test (from {len(images)} total)"
        )

    print(f"\n✅ Test set created successfully!")
    print(f"   Test folder: {test_path}")
    print(f"   Total test images: {total_test_images}")
    print(f"   Classes: {len(test_stats)}")

    return test_stats


# ============================================
# FUNCTION: VALIDATE TEST SET
# ============================================
def validate_test_set(test_path):
    """Validate that test set exists and has images"""
    print("\n" + "=" * 60)
    print("🔍 VALIDATING TEST SET")
    print("=" * 60)

    if not os.path.exists(test_path):
        print(f"❌ Test folder not found: {test_path}")
        return False

    class_folders = [
        d for d in os.listdir(test_path) if os.path.isdir(os.path.join(test_path, d))
    ]

    if len(class_folders) == 0:
        print(f"❌ Test folder is empty: {test_path}")
        return False

    total_images = 0
    print("\n📊 Test set contents:")
    for class_name in class_folders:
        class_path = os.path.join(test_path, class_name)
        num_images = len(
            [
                f
                for f in os.listdir(class_path)
                if f.endswith((".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"))
            ]
        )
        total_images += num_images
        print(f"   {class_name}: {num_images} images")

    print(f"\n✅ Test set validated: {total_images} total images")
    return True


# ============================================
# MODIFIED: Create data generators (now includes test set)
# ============================================
def create_data_generators():
    """Create data generators for training, validation, and testing"""

    # Define paths
    train_path = DATASET_PATH
    parent_dir = os.path.dirname(DATASET_PATH)
    test_path = os.path.join(parent_dir, "test")

    # Create test set from training data if it doesn't exist
    if not os.path.exists(test_path) or len(os.listdir(test_path)) == 0:
        print("\n⚠️ Test folder is empty or doesn't exist!")
        print("📁 Creating test set from training data...")
        create_test_set(train_path, test_path, test_size=0.15)
    else:
        print("\n✅ Test folder already exists, validating...")
        validate_test_set(test_path)

    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
        validation_split=0.2,  # Use 20% for validation from training data
    )

    # Only rescaling for validation (no augmentation)
    val_datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

    # Test datagen (no augmentation, no splitting)
    test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    # Get class names from training folder
    class_folders = [
        d
        for d in os.listdir(train_path)
        if os.path.isdir(os.path.join(train_path, d)) and d not in ["__pycache__"]
    ]

    # Training generator (80% of training data)
    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        classes=class_folders,
    )

    # Validation generator (20% of training data)
    val_generator = val_datagen.flow_from_directory(
        train_path,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        classes=class_folders,
    )

    # Test generator (from separate test folder)
    test_generator = test_datagen.flow_from_directory(
        test_path,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,  # Don't shuffle for evaluation
        classes=class_folders,
    )

    return train_generator, val_generator, test_generator, class_folders


def create_mobilenet_model(num_classes):
    """Create MobileNetV2 model (lightweight and efficient)"""

    # Using MobileNetV2 as base model
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights="imagenet"
    )

    # Freeze base model layers
    base_model.trainable = False

    model = models.Sequential(
        [
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    return model


def create_custom_cnn(num_classes):
    """Create custom CNN model (simpler, no external weights)"""

    model = models.Sequential(
        [
            layers.Conv2D(32, (3, 3), activation="relu", input_shape=(224, 224, 3)),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(512, activation="relu"),
            layers.Dense(256, activation="relu"),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    return model


def train_model(model, train_generator, val_generator):
    """Train the model"""

    # Compile the model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()],
    )

    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor="val_loss", patience=10, restore_best_weights=True, verbose=1
        ),
        ModelCheckpoint(
            "best_maize_model.h5",
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.2, patience=5, min_lr=0.00001, verbose=1
        ),
    ]

    # Train the model
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1,
    )

    return history


def plot_training_history(history):
    """Plot training history"""

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Plot accuracy
    axes[0].plot(history.history["accuracy"], label="Training Accuracy", linewidth=2)
    axes[0].plot(
        history.history["val_accuracy"], label="Validation Accuracy", linewidth=2
    )
    axes[0].set_title("Model Accuracy", fontsize=14)
    axes[0].set_xlabel("Epoch", fontsize=12)
    axes[0].set_ylabel("Accuracy", fontsize=12)
    axes[0].legend()
    axes[0].grid(True)

    # Plot loss
    axes[1].plot(history.history["loss"], label="Training Loss", linewidth=2)
    axes[1].plot(history.history["val_loss"], label="Validation Loss", linewidth=2)
    axes[1].set_title("Model Loss", fontsize=14)
    axes[1].set_xlabel("Epoch", fontsize=12)
    axes[1].set_ylabel("Loss", fontsize=12)
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.savefig("training_history.png", dpi=100)
    plt.show()
    print("\n📊 Training history saved as 'training_history.png'")


# ============================================
# MODIFIED: Evaluate model on test set
# ============================================
def evaluate_model(model, test_generator, class_names):
    """Evaluate the model on test data"""

    print("\n" + "=" * 60)
    print("📈 EVALUATING MODEL ON TEST SET")
    print("=" * 60)

    # Evaluate
    results = model.evaluate(test_generator, verbose=1)

    print(f"\n📊 Test Set Results:")
    print(f"   Loss: {results[0]:.4f}")
    print(f"   Accuracy: {results[1]:.4f} ({results[1]*100:.2f}%)")
    if len(results) > 2:
        print(f"   Precision: {results[2]:.4f}")
    if len(results) > 3:
        print(f"   Recall: {results[3]:.4f}")

    return results


def save_model_for_app(model, class_names, folder_to_display):
    """Save model in format ready for Flask app"""

    # Create models directory if it doesn't exist
    os.makedirs("app/models", exist_ok=True)

    # Save in H5 format
    model.save("maize_disease_model.h5")
    print("✅ Model saved as 'maize_disease_model.h5'")

    # Copy to app/models folder
    import shutil

    shutil.copy("maize_disease_model.h5", "app/models/maize_disease_model.h5")
    print("✅ Model copied to 'app/models/maize_disease_model.h5'")

    # Save class names with display names
    import json

    class_mapping = {
        "class_names": class_names,
        "display_names": [folder_to_display.get(name, name) for name in class_names],
        "folder_to_display": folder_to_display,
    }

    with open("class_names.json", "w") as f:
        json.dump(class_mapping, f, indent=2)
    print("✅ Class names saved as 'class_names.json'")

    # Also save for the app
    with open("app/models/class_names.json", "w") as f:
        json.dump(class_mapping, f, indent=2)
    print("✅ Class names copied to 'app/models/class_names.json'")

    # Convert to TensorFlow Lite
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()

        with open("maize_disease_model.tflite", "wb") as f:
            f.write(tflite_model)
        print("✅ TensorFlow Lite model saved as 'maize_disease_model.tflite'")
    except Exception as e:
        print(f"⚠️ TFLite conversion skipped: {e}")


def predict_sample(model, image_path, class_names, folder_to_display):
    """Test prediction on a single image"""
    from PIL import Image

    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = model.predict(img_array, verbose=0)
    predicted_class = np.argmax(predictions[0])
    confidence = np.max(predictions[0]) * 100

    folder_name = class_names[predicted_class]
    display_name = folder_to_display.get(folder_name, folder_name)

    print(f"\n🔬 Sample Prediction:")
    print(f"   Image: {os.path.basename(image_path)}")
    print(f"   Predicted: {display_name}")
    print(f"   Confidence: {confidence:.2f}%")

    return predicted_class, confidence


def main():
    """Main training function"""

    print("\n" + "=" * 60)
    print("🚀 STARTING MODEL TRAINING")
    print("=" * 60)

    # Create data generators (this will also create test set if needed)
    print("\n📂 Loading dataset and creating test set...")
    train_generator, val_generator, test_generator, class_names = (
        create_data_generators()
    )

    print(f"\n📊 Training samples: {train_generator.samples}")
    print(f"📊 Validation samples: {val_generator.samples}")
    print(f"📊 Test samples: {test_generator.samples}")
    print(f"🏷️ Number of classes: {train_generator.num_classes}")
    print(f"📋 Classes: {train_generator.class_indices}")

    # Ask user which model to use
    print("\n🤖 Choose model type:")
    print("   1. MobileNetV2 (Recommended - faster, more accurate)")
    print("   2. Custom CNN (Simpler, no pre-trained weights)")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "2":
        print("\n🏗️ Creating Custom CNN model...")
        model = create_custom_cnn(train_generator.num_classes)
    else:
        print("\n🏗️ Creating MobileNetV2 model...")
        model = create_mobilenet_model(train_generator.num_classes)

    model.summary()

    # Train model
    print("\n🚀 Starting training... (This may take several minutes)")
    history = train_model(model, train_generator, val_generator)

    # Plot results
    print("\n📊 Plotting training history...")
    plot_training_history(history)

    # Evaluate model on test set (not validation set!)
    print("\n📈 Evaluating model on test set...")
    evaluate_model(model, test_generator, class_names)

    # Save model
    print("\n💾 Saving model...")
    save_model_for_app(model, class_names, FOLDER_TO_DISPLAY)

    # Test prediction on a sample image from test set
    print("\n🔬 Testing model with sample prediction from test set...")

    # Get first image from test set
    parent_dir = os.path.dirname(DATASET_PATH)
    test_path = os.path.join(parent_dir, "test")

    for class_name in class_names:
        class_path = os.path.join(test_path, class_name)
        if os.path.exists(class_path):
            images = [
                f
                for f in os.listdir(class_path)
                if f.endswith((".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"))
            ]
            if images:
                sample_image = os.path.join(class_path, images[0])
                predict_sample(model, sample_image, class_names, FOLDER_TO_DISPLAY)
                break

    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📁 Files created:")
    print("   1. maize_disease_model.h5 - Trained model")
    print("   2. class_names.json - Class mapping")
    print("   3. training_history.png - Training graphs")
    print("   4. app/models/maize_disease_model.h5 - Model for Flask app")
    print(f"   5. dataset/test/ - Test set with {test_generator.samples} images")
    print("\n🎯 Next steps:")
    print("   1. Your test folder is now populated with images!")
    print("   2. Restart your Flask application")
    print("   3. The model will automatically load and use for predictions")
    print("   4. Test with new maize leaf images")


if __name__ == "__main__":
    main()
