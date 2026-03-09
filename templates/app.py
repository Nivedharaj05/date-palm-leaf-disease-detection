from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 1. Set upload folder path
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 2. Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 3. Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 4. Image upload route
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if file is present in the request
        if 'file' not in request.files:
            return render_template('Upload.html', message="No file part in the request")

        file = request.files['file']

        # Check if filename is empty
        if file.filename == '':
            return render_template('Upload.html', message="No file selected")

        # If file is valid and allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Pass filename to the template for preview
            return render_template('Upload.html', filename=filename, message="Image uploaded successfully!")

    return render_template('Upload.html')

if __name__ == "__main__":
    app.run(debug=True)
