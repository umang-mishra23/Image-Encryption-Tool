from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from encryption import encrypt_image, decrypt_image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image_file = request.files.get('image')
        key = request.form.get('key')
        method = request.form.get('method')
        mode = request.form.get('mode')  # Encrypt or Decrypt

        if not image_file or not key or not method or not mode:
            return render_template('index.html', error="Please upload an image, enter a key, choose a method, and select a mode.")

        # Save uploaded image
        filename = secure_filename(image_file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(input_path)

        # Prepare output path
        result_filename = f'{mode}_{method}_{filename}'
        result_path = os.path.join(RESULT_FOLDER, result_filename)

        try:
            # Call encryption or decryption function
            if mode == "encrypt":
                encrypt_image(input_path, result_path, key, method)
            elif mode == "decrypt":
                decrypt_image(input_path, result_path, key, method)
            else:
                return render_template('index.html', error="Invalid mode selected.")
        except Exception as e:
            return render_template('index.html', error=f"{mode.capitalize()}ion failed: {str(e)}")

        # Show result page with download option
        return render_template('result.html', result_filename=result_filename)

    return render_template('index.html')

@app.route('/download/<path:filename>')
def download(filename):
    path = os.path.join(RESULT_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "File not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
