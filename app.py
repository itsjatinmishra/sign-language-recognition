from flask import Flask, render_template, request, jsonify
import numpy as np  #for import numpy library
import tensorflow as tf # for creating model
import cv2
# from PIL import Image
import os
import pyttsx3
import threading
import base64
import io

app = Flask(__name__)

# Load the trained model (Load once to optimize performance)
MODEL_PATH = os.path.join("model", "asl_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

# Define class labels
DATASET_PATH = "dataset/train"
class_labels = sorted(os.listdir(DATASET_PATH)) if os.path.exists(DATASET_PATH) else ["Hello", "ThankYou", "Water", "Yes", "No"]

# Ensure 'uploads' directory exists
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to preprocess image
def process_image(image):
    try:
        if isinstance(image, str):  # If file path
            img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
            if img is None:
                raise ValueError("Invalid image file.")
        else:  # If PIL Image from base64
            img = np.array(image.convert("L"))  # Convert PIL image to grayscale

        img = cv2.resize(img, (64, 64))  # Resize
        img = img / 255.0  # Normalize
        img = img.reshape(1, 64, 64, 1)  # Reshape
        return img
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

# Function to convert text to speech
def speak_text(text):
    def tts():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Speech synthesis error: {e}")

    threading.Thread(target=tts).start()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload")
def upload_page():
    return render_template("upload.html")

# @app.route("/camera")
# def camera_page():
#     return render_template("camera.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

# Prediction from uploaded image
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        file.save(file_path)
        img_array = process_image(file_path)
        prediction = model.predict(img_array)
        predicted_label_index = np.argmax(prediction)
        predicted_word = class_labels[predicted_label_index]

        speak_text(predicted_word)

        return jsonify({"prediction": predicted_word})

    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# Prediction from camera image
@app.route("/predict_camera", methods=["POST"])
def predict_camera():
    try:
        data = request.json.get("image", "")
        if not data:
            return jsonify({"error": "No image data received"}), 400

        # Extract Base64 Data & Decode
        header, encoded = data.split(",", 1)  
        image_data = base64.b64decode(encoded)  
        image = Image.open(io.BytesIO(image_data))  

        img_array = process_image(image)  
        prediction = model.predict(img_array)
        predicted_label_index = np.argmax(prediction)
        predicted_word = class_labels[predicted_label_index]

        speak_text(predicted_word)

        return jsonify({"prediction": predicted_word})

    except Exception as e:
        return jsonify({"error": f"Camera prediction error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
