# Kidney Disease Prediction System

A smart web application that predicts the stage of Chronic Kidney Disease (CKD) using user-submitted health data, image processing, and machine learning. It features voice assistant integration, PDF report generation, email notifications, and secure user login/signup.

---

## 🚀 Features

* User Authentication (Signup/Login with hashed passwords)
* Voice-activated Login, Registration, and Prediction
* Chronic Kidney Disease Stage Prediction using Random Forest
* Input via Web Form and Voice Assistant
* Image upload & processing (Grayscale, Threshold, Binary)
* Data visualization with animated graphs
* Email Notification with Prediction Report
* PDF Report Download with Graph

---

## 📊 Technologies Used

* **Backend**: Flask, Flask-Mail, Flask-SQLAlchemy
* **Frontend**: HTML, CSS (Bootstrap), Jinja2 Templates
* **ML Models**: Random Forest, SVM, KNN, Decision Tree, Naive Bayes (via scikit-learn)
* **Voice Assistant**: pyttsx3, SpeechRecognition, PyAudio
* **Image Processing**: OpenCV, scikit-image
* **Visualization**: matplotlib, Pillow
* **PDF Generation**: xhtml2pdf, ReportLab

---

## 🔧 Installation

### 1. Clone the Repository

```bash
https://github.com/yourusername/kidney-disease-voice-assistant.git
cd kidney-disease-voice-assistant
```

### 2. Set up a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install PyAudio on Windows (if needed)

```bash
pip install pipwin
pipwin install pyaudio
```

---

## 📂 Dataset

Place the CKD dataset in the following path:

```
dataset/kidney_disease.csv
```

You can download it from [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/chronic_kidney_disease).

---

## ⚖️ How to Use

### Run the Flask App

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

### Voice Assistant

* Login: Say "login"
* Register: Say "register"
* Fill CKD Form: Say "fill form"
* Mute/Unmute: Say "mute" or "unmute"
* Stop Assistant: Say "stop" or "exit"

---

## 📧 Email Configuration

Edit the following lines in `app.py`:

```python
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'
```

Ensure you enable **App Passwords** or allow less secure apps (not recommended).

---

## 📤 PDF Report

* Automatically generated after prediction
* Includes patient details, result, and plotted graph
* Downloadable via `/download_pdf` route

---

## 🌐 Routes Summary

* `/` - Home Page
* `/signup` - User Registration
* `/login` - User Login
* `/logout` - Logout
* `/upload` - Upload Image for Processing
* `/predict` - Predict CKD Stage
* `/download_pdf` - Download Result PDF
* `/start_voice` - Start Voice Assistant
* `/predict_voice` - Predict via Voice Input

---

## ⚠️ Disclaimer

This project is for educational and prototyping purposes. It is **not** intended for real medical diagnosis.

---

## 🎉 Acknowledgements

* UCI Machine Learning Repository for the dataset
* OpenCV & scikit-learn for enabling powerful ML + image processing
* Flask & the Python community 👍

## 📜 License

This project is licensed under the [MIT License](LICENSE) © 2025 Nishanth Kumar B S.
