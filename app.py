from flask import Flask, request, render_template, send_from_directory
from PIL import Image
import os
import requests

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

uploaded_images = []  # Global image list

# Resize and compress image
def process_image(image_file, filename):
    image = Image.open(image_file)
    image.thumbnail((1920, 1080))
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(local_path, optimize=True, quality=70)
    return local_path

@app.route('/')
def home():
    return render_template('upload_cloud.html')

@app.route('/upload', methods=['POST'])
def upload():
    image_file = request.files['image']
    filename = image_file.filename
    processed_path = process_image(image_file, filename)

    upload_to = request.form.get('upload_to')
    if upload_to == 'imgur':
        image_url = upload_to_imgur(processed_path)
    else:
        image_url = f"/{processed_path}"

    uploaded_images.append(image_url)
    return render_template(
        'upload_success.html',
        image_url=image_url,
        image_list=uploaded_images,
        image_count=len(uploaded_images)
    )

def upload_to_imgur(image_path):
    headers = {"Authorization": "Client-ID bd148863ac41901"}  # Replace with your own
    with open(image_path, 'rb') as f:
        response = requests.post(
            "https://api.imgur.com/3/image",
            headers=headers,
            files={'image': f}
        )
    return response.json()['data']['link']

@app.route('/gallery')
def gallery():
    return render_template('upload_success.html', image_list=uploaded_images, image_count=len(uploaded_images), image_url=None)

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
