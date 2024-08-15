import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes // security feature

# Function to process the image, classify it, and crop if clear
def process_image(file_path):
    model = YOLO("best.pt", "v8")

    # Predict with the model
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_image:
        temp_image.close()
        Image.open(file_path).save(temp_image.name)
        results = model.predict(source=temp_image.name, conf=0.4, save=True)

    blur_conf_threshold = 0.5
    clear_conf_threshold = 0.9

    # Initialize flags
    is_blur = False
    is_clear = False
    cropped_image_path = None

    # Process results
    for result in results[0].boxes:
        confidence = result.conf[0].item()  # Extract the confidence score
        if blur_conf_threshold <= confidence <= clear_conf_threshold:
            is_blur = True
        elif confidence > clear_conf_threshold:
            is_clear = True
            box = result.xyxy[0].tolist()  # Extract bounding box coordinates
            cropped_image_path = crop_image(file_path, box)

    # Return classification and cropped image
    if is_blur:
        return 'The image is blurry. Please reupload the image again!', None
    elif is_clear:
        return 'The image is clear', cropped_image_path
    else:
        return 'Not Detected! The image is uncertain. Please reupload the image again!', None

# Function to crop the image based on bounding box
def crop_image(file_path, box):
    image = Image.open(file_path)
    cropped_image = image.crop(box)
    cropped_image_path = os.path.join(tempfile.gettempdir(), 'cropped_image.png')
    cropped_image.save(cropped_image_path)
    return cropped_image_path

@app.route('/classify', methods=['POST'])
def classify_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    classification, cropped_image_path = process_image(temp_file_path)

    if cropped_image_path:
        return jsonify({
            'classification': classification,
            'cropped_image_url': request.url_root + 'cropped_image'
        })
    else:
        return jsonify({
            'classification': classification
        })

@app.route('/cropped_image', methods=['GET'])
def get_cropped_image():
    return send_file(os.path.join(tempfile.gettempdir(), 'cropped_image.png'))

if __name__ == "__main__":
    app.run(debug=True)
