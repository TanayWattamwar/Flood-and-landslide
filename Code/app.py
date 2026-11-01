"""Web app."""
import flask
from flask import Flask, render_template, request, redirect, url_for

import pickle
import base64
from training import prediction
import requests

# Email imports
import smtplib
from email.mime.text import MIMEText
app = flask.Flask(__name__)

data = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
# data = [{'name':'India', "sel": ""}]
months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": "selected"}]
cities = [{'name':'Delhi', "sel": "selected"}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""}, {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""}, {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}]

model = pickle.load(open("model.pickle", 'rb'))

@app.route("/")
@app.route('/index.html')
def index() -> str:
    """Base page."""
    return flask.render_template("index.html")

@app.route('/plots.html')
def plots():
    return render_template('plots.html')

@app.route('/heatmaps.html')
def heatmaps():
    return render_template('heatmaps.html')

@app.route('/chart.html')
def chart():
    return render_template('chart.html')

@app.route('/satellite.html')
def satellite():
    direc = "satellite_images/Delhi_July.png"
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text="Delhi in July 2025")

@app.route('/satellite.html', methods=['GET', 'POST'])
def satelliteimages():
    place = request.form.get('place')
    date = request.form.get('date')
    data = [{'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""}, {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}]
    months = [{"name":"May", "sel": ""}, {"name":"June", "sel": ""}, {"name":"July", "sel": ""}]
    for item in data:
        if item["name"] == place:
            item["sel"] = "selected"
    
    for item in months:
        if item["name"] == date:
            item["sel"] = "selected"

    text = place + " in " + date + " 2025"

    direc = "satellite_images/{}_{}.png".format(place, date)
    with open(direc, "rb") as image_file:
        image = base64.b64encode(image_file.read())
    image = image.decode('utf-8')
    return render_template('satellite.html', data=data, image_file=image, months=months, text=text)

@app.route('/predicts.html')
def predicts():
    return render_template('predicts.html', cities=cities, cityname="Information about the city")

@app.route('/predicts.html', methods=["GET", "POST"])
def get_predicts():
    try:
        cityname = request.form["city"]
        cities = [
            {'name':'Delhi', "sel": ""}, {'name':'Mumbai', "sel": ""}, {'name':'Kolkata', "sel": ""},
            {'name':'Bangalore', "sel": ""}, {'name':'Chennai', "sel": ""}, {'name':'New York', "sel": ""},
            {'name':'Los Angeles', "sel": ""}, {'name':'London', "sel": ""}, {'name':'Paris', "sel": ""},
            {'name':'Sydney', "sel": ""}, {'name':'Beijing', "sel": ""}
        ]
        for item in cities:
            if item['name'] == cityname:
                item['sel'] = 'selected'

        print(f"Selected city: {cityname}")

        # OpenCage API
        URL = "https://api.opencagedata.com/geocode/v1/json"
        api_key = "ea7267a004eb40e0a7d488d4abfec2f8"
        PARAMS = {"q": cityname, "key": api_key}

        # sending get request
        r = requests.get(url=URL, params=PARAMS)
        print(r)
        data = r.json()

        if not data['results']:
            raise Exception("No results found from Database")

        latitude = data['results'][0]['geometry']['lat']
        longitude = data['results'][0]['geometry']['lng']
        print(f"Latitude: {latitude}, Longitude: {longitude}")

        # Get weather/prediction data
        final = prediction.get_data(latitude, longitude)

        final[4] *= 15
        if str(model.predict([final])[0]) == "0":
            pred = "Safe"
        else:
            pred = "Unsafe"

        return render_template(
            'predicts.html',
            cityname="Information about " + cityname,
            cities=cities,
            temp=round(final[0], 2),
            maxt=round(final[1], 2),
            wspd=round(final[2], 2),
            cloudcover=round(final[3], 2),
            percip=round(final[4], 2),
            humidity=round(final[5], 2),
            pred=pred
        )

    except Exception as e:
        print(f"Error: {e}")
        return render_template(
            'predicts.html',
            cities=cities,
            cityname="Oops, we weren't able to retrieve data for that city."
        )
    
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    full_message = f"""
    Name: {name}
    Email: {email}
    Subject: {subject}
    Message: {message}
    """

    msg = MIMEText(full_message)
    msg['Subject'] = "New Contact Form Message"
    msg['From'] = email
    msg['To'] = "kartiknalawade246@gmail.com"  # 🔴 CHANGE THIS

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("kartiknalawade246@gmail.com", "dfukuutbmgattlrv")  # 🔴 CHANGE
        server.send_message(msg)
        server.quit()

        return "OK"

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)