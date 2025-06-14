import pyttsx3
import speech_recognition as sr
import webbrowser
import threading
import requests
import subprocess

stop_flag = False
is_muted = False  # ✅ Global mute toggle

def speak(text, force=False):
    if not is_muted or force:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        print(f"[Muted] {text}")

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening for command...")
        r.adjust_for_ambient_noise(source, duration=0.5)  # Handle background noise
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
            print("🧠 Processing audio...")
            query = r.recognize_google(audio, language="en-IN")  # Indian accent support
            print(f"🗣 User said: {query}")
            return query.lower().strip()
        except sr.UnknownValueError:
            print("❓ Could not understand the audio.")
            return ""
        except sr.RequestError:
            print("❗ API unavailable.")
            return ""
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out.")
            return ""

def collect_ckd_form_data():
    fields = {
        "age": "your age",
        "bp": "your blood pressure",
        "sg": "specific gravity",
        "al": "albumin level",
        "su": "sugar level",
        "rbc": "red blood cells status, say 1 for normal, 0 for abnormal",
        "pc": "pus cell status, say 1 for normal, 0 for abnormal",
        "pcc": "pus cell clumps, say 1 for present, 0 for not present",
        "ba": "bacteria, say 1 for present, 0 for not present",
        "bgr": "blood glucose random",
        "bu": "blood urea",
        "sc": "serum creatinine",
        "sod": "sodium",
        "pot": "potassium",
        "hemo": "hemoglobin level",
        "pcv": "packed cell volume",
        "wc": "white blood cell count",
        "rc": "red blood cell count"
    }

    data = {}
    for key, prompt in fields.items():
        speak(f"Please tell me {prompt}")
        value = listen()
        data[key] = value
    return data

def handle_ckd_prediction(username="User"):
    speak("Let's fill out your CKD prediction form.")
    data = collect_ckd_form_data()

    try:
        response = requests.post("http://127.0.0.1:5000/predict_voice", json=data)
        if response.ok:
            result = response.json().get("result", None)
            if result is not None:
                result = int(result)
                stages = {
                    0: "You have severe chronic kidney disease which is at Stage I.",
                    1: "You have severe chronic kidney disease which is at Stage II.",
                    2: "You have severe chronic kidney disease which is at Stage III.",
                    3: "You have severe chronic kidney disease which is at Stage IV.",
                    4: "You have severe chronic kidney disease which is at Stage V.",
                }
                stage_text = stages.get(result, "You have no signs of Chronic Kidney Disease.")
                speak(f"Hello {username}, your prediction result is: {stage_text}")
                speak(f"Hello {username}, your prediction result has been sent to your mail.")
            else:
                speak("No result received.")
        else:
            speak("Sorry, there was a problem submitting the form.")
    except Exception as e:
        print(f"Error: {e}")
        speak("An error occurred while connecting to the server.")

def voice_registration():
    speak("Please say your username")
    username = listen()

    speak("Please say your email")
    email_input = listen()
    email = email_input.strip().replace(" ", "").lower()
    if "@gmail.com" not in email:
        email += "@gmail.com"

    speak("Please say your password")
    password = listen()

    try:
        response = requests.post("http://127.0.0.1:5000/register", data={
            "username": username,
            "email": email,
            "password": password
        })
        if response.ok:
            speak(f"Welcome {username}, your account has been created.")
        else:
            speak("There was an error registering. Please try again.")
    except Exception as e:
        print(e)
        speak("Failed to connect to registration server.")

def voice_login():
    speak("Please say your username")
    username = listen()

    speak("Please say your email")
    email_input = listen()
    email = email_input.strip().replace(" ", "").lower()
    if "@gmail.com" not in email:
        email += "@gmail.com"

    speak("Please say your password")
    password = listen()

    try:
        response = requests.post("http://127.0.0.1:5000/login", data={
            "username": username,
            "email": email,
            "password": password
        })
        if response.ok and "Welcome" in response.text:
            speak(f"Welcome back {username}, you are now logged in.")
        else:
            speak("Login failed. Please try again.")
    except Exception as e:
        print(e)
        speak("Failed to connect to the server.")

def start_voice_login_thread():
    thread = threading.Thread(target=voice_login)
    thread.start()

def start_voice_registration_thread():
    thread = threading.Thread(target=voice_registration)
    thread.start()

def run_voice_assistant(username=None):
    global stop_flag, is_muted
    stop_flag = False

    if username:
        speak(f"Hi {username}, welcome to the Kidney Disease Predictor System.")
    else:
        speak("Hello, I am your voice assistant. How can I help you today?")

    while not stop_flag:
        query = listen()

        if "report" in query:
            speak("Opening your report page.")
            webbrowser.open("http://localhost:5000/predict")

        elif "logout" in query:
            speak("Logging you out.")
            webbrowser.open("http://localhost:5000/logout")
        
        elif "login" in query:
            speak("Redirecting you to the login page.")
            webbrowser.open("http://localhost:5000/login")

        elif "register" in query or "sign up" in query:
            voice_registration()

        elif "help" in query:
            speak("You can say commands like report, logout, fill form, register, mute, unmute, or stop.")

        elif "fill form" in query or "ckd form" in query or "kidney form" in query:
            handle_ckd_prediction(username)

        elif "mute" in query:
            is_muted = True
            print("[Muted]")

        if "unmute" in query:
            is_muted = False
            print("[Unmuted]")
            speak("Assistant unmuted. Hello, I am your voice assistant. How can I help you today?", force=True)
            
        elif "stop" in query or "exit" in query or "bye" in query:
            if username:
                speak(f"Thank you {username}. Goodbye!")
            else:
                speak("Thank you. Goodbye!")
            stop_flag = True
            break

        elif query:
            speak("Sorry, I didn’t understand that. Please say help to know available commands.")

def start_voice_assistant_thread(username=None):
    thread = threading.Thread(target=run_voice_assistant, args=(username,))
    thread.start()

def stop_voice_assistant():
    global stop_flag
    stop_flag = True
