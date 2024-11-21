from flask import Flask, render_template, request, make_response
from models import Model # type: ignore
from writeCsv import write_to_csv # type: ignore
from datetime import datetime
import os, random
import pandas as pd
import numpy as np
import cv2
import glob
from werkzeug.utils import secure_filename
import json

from skimage import measure
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.debug = True

# Routes for Kidney Disease Prediction
@app.route('/')
def root():
    return render_template('index.html')

@app.route('/predict', methods=["POST"])
def predict():
    # Extract form values
    age = int(request.form['age'])
    bp = int(request.form['bp'])
    sugar = int(request.form['sugar'])
    pc = int(request.form['pc'])
    pcc = int(request.form['pcc'])
    sodium = int(request.form['sodium'])
    hemo = float(request.form['hemo'])
    htn = int(request.form['htn'])
    db = int(request.form['db'])

    # Prepare values for prediction
    values = [age, bp, sugar, pc, pcc, sodium, hemo, htn, db]
    print(values)

    # Predict using the model
    model = Model()
    classifier = model.randomforest_classifier()
    prediction = classifier.predict([values])
    print(f"Kidney disease = {prediction[0]}")

    # Log and save to CSV
    time = datetime.now().strftime("%m/%d/%Y (%H:%M:%S)")
    write_to_csv(time, age, bp, sugar, pc, pcc, sodium, hemo, htn, db, prediction[0])
    return render_template("result.html", result=prediction[0], sugar=sugar)

# Function to calculate Mean Squared Error between images
def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/uploadajax', methods=['POST'])
def upldfile():
    print("request :", str(request), flush=True)
    
    if request.method == 'POST':
        # Handle file upload
        prod_mas = request.files['first_image']
        filename = secure_filename(prod_mas.filename)
        filepath = os.path.join("D:\\Upload\\", filename)
        prod_mas.save(filepath)

        # Read and process the uploaded image
        ci = cv2.imread(filepath)
        gray = cv2.cvtColor(ci, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f"static/Grayscale/{filename}", gray)

        # Create HSV and binary images
        thresh = cv2.cvtColor(ci, cv2.COLOR_BGR2HSV)
        cv2.imwrite(f"static/Threshold/{filename}", thresh)
        
        hsv_img = cv2.cvtColor(ci, cv2.COLOR_BGR2HSV)
        lower_green = np.array([34, 177, 76])
        upper_green = np.array([255, 255, 255])
        binary = cv2.inRange(hsv_img, lower_green, upper_green)
        cv2.imwrite(f"static/Binary/{filename}", binary)

        # Read file size
        val = os.stat(filepath).st_size
        
        # Read the model data from the 'model.h5' file
        flist = []
        with open('model.h5') as f:
            for line in f:
                flist.append(line)

        # Search for the matching data by file size
        dataval = ''
        for line in flist:
            if str(val) in line:
                dataval = line.strip()  # Remove newline and any extra spaces
        
        # Process the data if found
        if dataval:
            strv = dataval.split('-')

            # Safely access list elements with error handling
            op = str(strv[3]) if len(strv) > 3 else "Unknown"
            stg = str(strv[17]) if len(strv) > 17 else "Not Available"
            acc = str(strv[2]) if len(strv) > 2 else "Unknown"
        else:
            op, stg, acc = "Unknown", "Not Applicable", "Unknown"

        if op == 'Normal':
            stg = 'Not Applicable'

        # Compare uploaded image to dataset
        diseaselist = os.listdir('static/Dataset')
        width, height = 400, 400
        dim = (width, height)
        oresized = cv2.resize(ci, dim, interpolation=cv2.INTER_AREA)

        # Loop through disease dataset and compare images
        flagger = True
        for disease in diseaselist:
            if flagger:
                files = glob.glob(f'static/Dataset/{disease}/*')
                for file in files:
                    oi = cv2.imread(file)
                    resized = cv2.resize(oi, dim, interpolation=cv2.INTER_AREA)

        # Prepare and return the response
        msg = f"{op},{filename},{acc},{stg}"
        resp = make_response(json.dumps(msg))
        return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0')
