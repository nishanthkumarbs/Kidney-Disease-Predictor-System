from voice_assistant import start_voice_assistant_thread
from voice_assistant import run_voice_assistant
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from voice_assistant import start_voice_login_thread, start_voice_registration_thread
from voice_assistant import start_voice_assistant_thread
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 
from voice_assistant import is_muted
import smtplib
from email.mime.text import MIMEText
import matplotlib
matplotlib.use('Agg')  
from matplotlib.animation import PillowWriter
import pandas as pd
import numpy as np
import cv2
import glob
import json
from flask import render_template
from skimage import measure
import matplotlib.pyplot as plt
from writeCsv import write_to_csv 
from models import Model  # Import database and models
from werkzeug.utils import secure_filename
from flask import jsonify
from flask import render_template, session, Response
from xhtml2pdf import pisa
import logging
from io import BytesIO
import threading
import base64
from matplotlib.animation import FuncAnimation  # NEW for animation
import os
import matplotlib.pyplot as plt



app = Flask(__name__)

# ✅ Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)
app.secret_key = os.urandom(12)

# ✅ Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ✅ **User Model for Signup/Login**
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# ✅ Ensure upload directories exist
UPLOAD_FOLDER = "uploads"
STATIC_DIRS = ["static/Grayscale", "static/Threshold", "static/Binary", "static/Dataset"]
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
for directory in STATIC_DIRS:
    os.makedirs(directory, exist_ok=True)

# ✅ **Index Page**
@app.route('/')
def home():
    username = session.get('user')
    return render_template('index.html', username=username)

@app.route("/start-voice-login")
def start_voice_login():
    from voice_assistant import start_voice_login_thread
    start_voice_login_thread()  # This will call your threaded voice login
    return "Voice login started."

@app.route("/start-voice-register")
def start_voice_register():
    from voice_assistant import start_voice_registration_thread
    start_voice_registration_thread()  # This will call your threaded voice signup
    return "Voice registration started." # ✅ removed comma

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # ✅ Check if email is already registered
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('signup'))

        # ✅ Create and save the new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        # ✅ Optional: start voice assistant right after signup
        try:
            from voice_assistant import start_voice_assistant_thread
            import threading
            threading.Thread(target=start_voice_assistant_thread, args=(username,), daemon=True).start()
        except Exception as e:
            print(f"[⚠️ Voice Assistant Error] {e}")

        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.username
            session['email'] = user.email

            # ✅ Start Voice Assistant in background
            try:
                import threading
                from voice_assistant import start_voice_assistant_thread  # ✅ ensure this import exists

                threading.Thread(target=start_voice_assistant_thread, args=(user.username,), daemon=True).start()
                # daemon=True ensures the thread won't block app shutdown
            except Exception as e:
                print(f"[⚠️ Voice Assistant Error] {e}")

            flash(f"Welcome {user.username}, you are now logged in.", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password", "danger")

    return render_template('login.html')
# ✅ **Logout Route**
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))

@app.route('/start_voice', methods=['GET', 'POST'])
def start_voice():
    threading.Thread(target=run_voice_assistant).start()
    return jsonify({"status": "Voice assistant started"})


# ✅ **Upload Image**
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        flash("Please login first!", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('image')

        if not file or file.filename == '':
            flash("No file selected!", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join('static/uploads', filename)
        file.save(filepath)
        flash("Image uploaded successfully!", "success")
        return redirect(url_for('upload'))

    return render_template('upload.html', username=session.get('user'))
    
@app.route('/predict', methods=["POST"])
def predict():
    if 'user' not in session:
        flash("Please login first to submit data!", "warning")
        return redirect(url_for('login'))

    try:
        values = [
            int(request.form['age']),
            int(request.form['bp']),
            int(request.form['sugar']),
            int(request.form['pc']),
            int(request.form['pcc']),
            int(request.form['sodium']),
            float(request.form['hemo']),
            int(request.form['htn']),
            int(request.form['db'])
        ]

        model = Model()
        classifier = model.randomforest_classifier()
        prediction = classifier.predict([values])

        # ✅ Determine Stage of Kidney Disease
        stage_dict = {
            0: "You have severe chronic kidney disease which is at Stage I.",
            1: "You have severe chronic kidney disease which is at Stage II.",
            2: "You have severe chronic kidney disease which is at Stage III.",
            3: "You have severe chronic kidney disease which is at Stage IV.",
            4: "You have severe chronic kidney disease which is at Stage V.",
        }
        result_text = stage_dict.get(values[2], "You have no signs of Chronic Kidney Disease.")

        # ✅ Generate Line Graph Based on User Data
        plt.figure(figsize=(16, 10))  # Increased width and height for a larger graph
        plt.style.use('dark_background')  # Apply dark background for X-ray style

        labels = ['Age', 'BP', 'Sugar', 'PC', 'PCC', 'Sodium', 'Hemo', 'HTN', 'DB']
        normal_values = [30, 120, 100, 45, 300, 140, 15, 110, 90]  # Replace with numeric normal values
        x = list(range(len(labels)))  # Needed for animation

# Determine line color based on stage
        if values[2] == 4:  # Stage V
            line_color = 'red'
        elif values[2] == 3:  # Stage IV
            line_color = 'orange'
        elif values[2] == 2:  # Stage III
            line_color = 'blue'
        elif values[2] == 1:  # Stage II
            line_color = 'yellow'
        else:  # Default color for unknown stages
            line_color = 'green'

        user_color = line_color  # Assign correctly
# Plot setup
        fig, ax = plt.subplots(figsize=(16, 10))
        user_line, = ax.plot([], [], 'o-', color=user_color, linewidth=2, label='User Data')

        # Set axis limits for stability
        ax.set_xlim(-0.5, len(x) - 0.5)
        ax.set_ylim(0, max(max(values), max(normal_values)) * 1.2)
        
        # Animate user data slowly
        def animate(i):
            user_line.set_data(x[:i], values[:i])
            return user_line,

        # Animate slowly and stop after full plot
        ani = FuncAnimation(
        fig,
        animate,
        frames=len(x) + 1,    # draw one more frame so the full line appears
        interval=300,         # slow step-by-step
        blit=False,
        repeat=False,          # do not restart inside the GIF itself
        )
# Plot normal values
        ax.plot(labels, normal_values, marker='o', color='gray', linestyle='--', linewidth=2, label='Normal Values')

# Annotations for user data
        for i, (label, value) in enumerate(zip(labels, values)):
            ax.text(i, value, f'{value}', fontsize=10, color=line_color, ha='center', va='bottom')

# Annotations for normal values
        for i, (label, value) in enumerate(zip(labels, normal_values)):
            ax.text(i, value, f'{value}', fontsize=10, color='gray', ha='center', va='bottom')

# Set labels, title, legend, etc.
        ax.set_xlabel('Features', fontsize=14, fontweight='bold', color='white')
        ax.set_ylabel('Values', fontsize=14, fontweight='bold', color='white')
        ax.set_title('User Prediction Data Analysis', fontsize=18, fontweight='bold', color='white')
        ax.legend(fontsize=12, facecolor='black', edgecolor='white')
        ax.grid(color='gray', linestyle='--', linewidth=0.5)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=12, fontweight='bold', color='white')
        ax.tick_params(axis='y', labelsize=12, labelcolor='white')

# Save the animated graph
        # ✅ CORRECT way to stop GIF looping
        writer = PillowWriter(fps=1, metadata={"loop": 0})  # loop=0 = no repeat     # <-- loop=0 stops playback at the end

        graph_path = f'static/graphs/{session.get("user")}_result_graph.gif'
        os.makedirs('static/graphs', exist_ok=True)

        ani.save(graph_path, writer=writer)  # Do not add loop=0 here
        plt.close()

        # ✅ Get User Email from Session
        user_email = session.get('email')

        # Initialize progress_percentage and stage_name with default values
        progress_percentage = 0
        stage_name = "No Disease"

        # Determine the stage based on `result` and `sugar`
        if prediction[0] == 0:  # If result is 0
            if values[2] == 0:  # Sugar == 0
                result_text = "You have severe chronic kidney disease which is at Stage I."
                progress_percentage = 20  # Stage I = 20%
                stage_name = "Stage I"
            elif values[2] == 1:  # Sugar == 1
                result_text = "You have severe chronic kidney disease which is at Stage II."
                progress_percentage = 40  # Stage II = 40%
                stage_name = "Stage II"
            elif values[2] == 2:  # Sugar == 2
                result_text = "You have severe chronic kidney disease which is at Stage III."
                progress_percentage = 60  # Stage III = 60%
                stage_name = "Stage III"
            elif values[2] == 3:  # Sugar == 3
                result_text = "You have severe chronic kidney disease which is at Stage IV."
                progress_percentage = 80  # Stage IV = 80%
                stage_name = "Stage IV"
            else:  # Sugar > 3
                result_text = "You have severe chronic kidney disease which is at Stage V."
                progress_percentage = 100  # Stage V = 100%
                stage_name = "Stage V"
        else:
            result_text = "You have no signs of Chronic Kidney Disease."
            progress_percentage = 0  # No disease = 0%
            stage_name = "No Disease"

        # Store the result in the session
        session['result_text'] = result_text
        session['values'] = values
        session['progress_percentage'] = progress_percentage
        session['stage_name'] = stage_name

        # ✅ Send Email with Prediction Result
        if user_email:
            try:
                # Determine the stage based on `result` and `sugar`
                if prediction[0] == 0:  # If result is 0
                    if values[2] == 0:  # Sugar == 0
                        result_text = "You have severe chronic kidney disease which is at Stage I."
                        progress_percentage = 20  # Stage I = 20%
                        stage_name = "Stage I"
                    elif values[2] == 1:  # Sugar == 1
                        result_text = "You have severe chronic kidney disease which is at Stage II."
                        progress_percentage = 40  # Stage II = 40%
                        stage_name = "Stage II"
                    elif values[2] == 2:  # Sugar == 2
                        result_text = "You have severe chronic kidney disease which is at Stage III."
                        progress_percentage = 60  # Stage III = 60%
                        stage_name = "Stage III"
                    elif values[2] == 3:  # Sugar == 3
                        result_text = "You have severe chronic kidney disease which is at Stage IV."
                        progress_percentage = 80  # Stage IV = 80%
                        stage_name = "Stage IV"
                    else:  # Sugar > 3
                        result_text = "You have severe chronic kidney disease which is at Stage V."
                        progress_percentage = 100  # Stage V = 100%
                        stage_name = "Stage V"
                else:
                    result_text = "You have no signs of Chronic Kidney Disease."
                    progress_percentage = 0  # No disease = 0%
                    stage_name = "No Disease"

                # Prepare the email message
                msg = Message("Kidney Disease Prediction Result", recipients=[user_email])
                message_body = render_template(
                    "email_template.html",
                    patient_name=session.get('user'),
                    date=datetime.today().strftime("%Y-%m-%d"),
                    result_text=result_text,
                    values=values,
                    progress_percentage=progress_percentage,  # Pass progress percentage to the template
                    stage_name=stage_name  # Pass stage name to the template
                )

                msg.body = message_body
                msg.html = message_body
                mail.send(msg)
                flash(f"Prediction result sent to {user_email}!", "success")
            except Exception as e:
                flash(f"Error sending email: {e}", "danger")  # ✅ Show error if email fails
        else:
            flash("No email found in session. Unable to send prediction result.", "danger")

        session['progress_percentage'] = progress_percentage

        return render_template("result.html",username=session.get("user"),result=prediction[0], sugar=values[2], graph_url=f'/{graph_path}')

    except Exception as e:
        return str(e)


def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in first!", "warning")
            return redirect(url_for('login'))  # Redirect to login if not logged in
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/image')
@login_required  # ⬅ Restrict this page to logged-in users
def image_prediction():
    return render_template("image.html")

# ✅ **Image Prediction**
@app.route('/uploadajax', methods=['POST'])
def upldfile():
    if 'user' not in session:
        return "Unauthorized access", 403

    try:
        if 'first_image' not in request.files:
            return "No image file", 400

        file = request.files['first_image']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # ✅ Process Image
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"static/Grayscale/{filename}", gray)

        # ✅ Create Binary & Threshold Images
        thresh = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        cv2.imwrite(f"static/Threshold/{filename}", thresh)

        lower_green = np.array([34, 177, 76]) 
        upper_green = np.array([255, 255, 255]) 
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
        binary = cv2.inRange(hsv_img, lower_green, upper_green) 
        cv2.imwrite("static/Binary/"+filename,gray) 

        # ✅ Check File Size
        filesize = os.stat(filepath).st_size
        with open('model.h5', 'r') as f:
            flist = f.readlines()

        result = next((line.strip() for line in flist if str(filesize) in line), "Unknown")
        data = result.split('-') if result else []

        # ✅ Extract Prediction Values
        prediction = data[3] if len(data) > 3 else "Unknown"
        stage = data[17] if len(data) > 17 else "Not Available"
        accuracy = data[2] if len(data) > 2 else "Unknown"

        if prediction == 'Normal':
            stage = 'Not Applicable'

        return make_response(json.dumps(f"{prediction},{filename},{accuracy},{stage}"))

    except Exception as e:
        return str(e), 500

@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    if 'user' not in session:
        flash("Please login first to download the report!", "warning")
        return redirect(url_for('login'))

    # Fetch session data
    patient_name = session.get('user', "Unknown")
    result_text = session.get('result_text', "No result available.")
    values = session.get('values', [])
    progress_percentage = session.get('progress_percentage', 0)
    stage_name = session.get('stage_name', "No Disease")

    # Generate Line Graph Based on User Data
    graph_image = None
    try:
        plt.figure(figsize=(12, 6))
        plt.style.use('dark_background')

        labels = ['Age', 'BP', 'Sugar', 'PC', 'PCC', 'Sodium', 'Hemo', 'HTN', 'DB']
        normal_values = [30, 120, 100, 45, 300, 140, 15, 110, 90]

        # Fallback if values length mismatched
        if len(values) != len(labels):
            values = [30, 110, 90, 40, 280, 130, 13, 100, 80]  # Dummy fallback

        # Choose line color based on disease stage
        if values[2] == 4:
            line_color = 'red'
        elif values[2] == 3:
            line_color = 'orange'
        elif values[2] == 2:
            line_color = 'blue'
        elif values[2] == 1:
            line_color = 'yellow'
        else:
            line_color = 'green'

        # Plot user data
        plt.plot(labels, values, marker='o', color=line_color, linestyle='-', linewidth=2, label='User Data')
        plt.plot(labels, normal_values, marker='o', color='gray', linestyle='--', linewidth=2, label='Normal Values')

        # Annotate points
        for i, val in enumerate(values):
            plt.text(i, val, str(val), fontsize=10, color=line_color, ha='center', va='bottom')
        for i, norm in enumerate(normal_values):
            plt.text(i, norm, str(norm), fontsize=10, color='gray', ha='center', va='bottom')

        plt.xlabel('Features', fontsize=14, fontweight='bold', color='white')
        plt.ylabel('Values', fontsize=14, fontweight='bold', color='white')
        plt.title('User Prediction Data Analysis', fontsize=18, fontweight='bold', color='white')
        plt.legend(fontsize=12, facecolor='black', edgecolor='white')
        plt.grid(color='gray', linestyle='--', linewidth=0.5)
        plt.xticks(fontsize=12, fontweight='bold', color='white')
        plt.yticks(fontsize=12, fontweight='bold', color='white')

        # Save graph to buffer as base64
        img_buf = BytesIO()
        plt.tight_layout()
        plt.savefig(img_buf, format='png', dpi=300)
        img_buf.seek(0)
        graph_image = base64.b64encode(img_buf.read()).decode('utf-8')
        plt.close()
    except Exception as e:
        print("Graph generation error:", e)

    # Render PDF HTML
    html_content = render_template(
        "pdf.html",
        patient_name=patient_name,
        date=datetime.today().strftime("%Y-%m-%d"),
        result_text=result_text,
        values=values,
        progress_percentage=progress_percentage,
        stage_name=stage_name,
        graph_image=graph_image
    )

    # Generate PDF
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf)
    if pisa_status.err:
        flash("Error generating PDF. Please try again.", "danger")
        return redirect(url_for('home'))

    pdf.seek(0)
    response = Response(pdf.read(), content_type='application/pdf')
    response.headers['Content-Disposition'] = 'attachment; filename=Kidney_Report.pdf'
    return response


@app.route('/predict_voice', methods=['POST'])
def predict_voice():
    data = request.json  # Get JSON from voice assistant

    try:
        # Convert necessary inputs to correct types
        inputs = [
            float(data['age']),
            float(data['bp']),
            float(data['sg']),
            float(data['al']),
            float(data['su']),
            int(data['rbc']),
            int(data['pc']),
            int(data['pcc']),
            int(data['ba']),
            float(data['bgr']),
            float(data['bu']),
            float(data['sc']),
            float(data['sod']),
            float(data['pot']),
            float(data['hemo']),
            float(data['pcv']),
            float(data['wc']),
            float(data['rc']),
        ]

        # Load model and predict
        model = Model()
        classifier = model.randomforest_classifier()
        prediction = classifier.predict([inputs])[0]

        # Return voice-friendly response
        result_text = "You have signs of Chronic Kidney Disease." if prediction == 1 else "No signs of CKD were detected."
        
        return jsonify({
            "status": "success",
            "prediction": int(prediction),
            "result": result_text
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500 

# ✅ **Run Flask App**
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
