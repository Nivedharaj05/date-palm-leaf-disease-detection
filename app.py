from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)
app.secret_key = 'datepalm123'

# === Paths & Folders ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR  = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'users.db')

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# === Helpers ===
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    """Ensure database folder exists, drop old users table, and create fresh one."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if not os.path.exists('users.db'):
    init_db()

MODEL_PATH = r"C:\DatePalmDisease\Trained_Models\MobileNetV2_New.h5"
model = load_model(MODEL_PATH)
class_names = ['Brown Spots', 'Healthy', 'White Scale']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        uname = request.form['username']
        mail  = request.form['email']
        pwd   = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (uname, mail, pwd)
            )
            conn.commit()
            flash("Signup successful. Please sign in.", "success")
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash("Username already exists. Try a different one.", "danger")
        finally:
            conn.close()
    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        uname = request.form['username']
        pwd   = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        cur  = conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (uname, pwd)
        )
        user = cur.fetchone()
        conn.close()
        if user:
            session['user'] = uname
            flash("Welcome back!", "success")
            return redirect(url_for('upload'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    result     = None
    filename   = None
    confidence = None

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in the request.", "danger")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected.", "warning")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                img = image.load_img(filepath, target_size=(224, 224))
                arr = image.img_to_array(img)
                arr = np.expand_dims(arr, axis=0) / 255.0

                pred = model.predict(arr)
                idx  = np.argmax(pred)
                result     = class_names[idx]
                confidence = round(100 * float(np.max(pred)), 2)

                flash(f"Prediction: {result} ({confidence}% confidence)", "info")
            except Exception as e:
                flash(f"Error during prediction: {e}", "danger")
                return redirect(request.url)
        else:
            flash("Invalid file format. Please upload a PNG or JPG image.", "danger")
            return redirect(request.url)

    return render_template('upload.html', result=result, filename=filename, confidence=confidence)


if __name__ == '__main__':
    app.run(debug=True)