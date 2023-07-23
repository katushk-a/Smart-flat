import random
import configparser
from flask import Flask, render_template, jsonify, request
import threading
import tkinter as tk
from tkinter import Tk, Label, StringVar
from flaskext.mysql import MySQL
import mysql.connector
import time

app = Flask(__name__)


app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234567890'
app.config['MYSQL_DATABASE_DB'] = 'my_database'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL(app)

@app.before_first_request
def create_database():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS my_database")
    cursor.execute("USE my_database")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS room_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            turn_on_temperature FLOAT,
            turn_off_temperature FLOAT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature_archive (
            id INT AUTO_INCREMENT PRIMARY KEY,
            temperature FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

def store_temperature_reading(temperature):
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO temperature_archive (temperature) VALUES (%s)", (temperature,))

    conn.commit()
    cursor.close()
    conn.close()

light1 = False
light2 = False
light3 = False
brightness3 = 50

config = configparser.ConfigParser()
config.read("config.ini")

if not config.sections():
    config["TEMPERATURE_THRESHOLDS"] = {"lower_threshold": 24.2, "upper_threshold": 25.1}
    with open("config.ini", "w") as configfile:
        config.write(configfile)

n1 = float(config["TEMPERATURE_THRESHOLDS"]["lower_threshold"])
n2 = float(config["TEMPERATURE_THRESHOLDS"]["upper_threshold"])

m1 = 9
m2 = 31
heating = False
temperature = round(random.uniform(m1, m2), 1)
def get_temp_reading():
    global temperature
    temperature = round(random.uniform(m1, m2), 1)
    store_temperature_reading(temperature)
    return temperature

def update_heating_system(temp):
    global heating
    if temp < n1:
        heating = True
    elif temp > n2:
        heating = False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/light-on")
def light_on():
    global light1
    light1 = True
    print("Light 1 turned on")
    return jsonify({"message": "Light 1 turned on", "light1": light1})

@app.route("/light-off")
def light_off():
    global light1
    light1 = False
    print("Light 1 turned off")
    return jsonify({"message": "Light 1 turned off", "light1": light1})

@app.route("/light-on2")
def light_on2():
    global light2
    light2 = True
    print("Light 2 turned on")
    return jsonify({"message": "Light 2 turned on", "light2": light2})

@app.route("/light-off2")
def light_off2():
    global light2
    light2 = False
    print("Light 2 turned off")
    return jsonify({"message": "Light 2 turned off", "light2": light2})

@app.route("/brightness-control3")
def brightness_control3():
    global brightness3
    brightness3 = int(request.args.get("brightness3"))
    print(f"Brightness 3 set to {brightness3}%")
    return jsonify({"message": f"Brightness 3 set to {brightness3}%", "brightness": brightness3})

@app.route("/get-temp-reading")
def get_temp_reading_route():
    global heating
    temp_reading = get_temp_reading()
    update_heating_system(temp_reading)
    return jsonify({"temp_reading": temp_reading, "heating_system": heating})

def run_gui():
    global heating, n1, n2
    root = Tk()
    root.title("Temperature Monitor")
    
    temperature_label = Label(root, text="Temperature: ")
    temperature_label.pack()

    heating_status_label = Label(root, text="Heating system: ")
    heating_status_label.pack()
    
    temperature_value = StringVar()
    temperature_value.set(f"{temperature} °C") 
    temperature_display = Label(root, textvariable=temperature_value)
    temperature_display.pack()

    heating_system_status = heating

    class TemperatureChart:
        def __init__(self, canvas, width, height, max_data_points=100, max_value=100):
            self.canvas = canvas
            self.width = width
            self.height = height
            self.max_data_points = max_data_points
            self.max_value = max_value
            self.data = []
            self.timestamps = []

        def add_data(self, temperature):
            self.data.append(temperature)
            if len(self.data) > self.max_data_points:
                self.data.pop(0)

        def update(self):
            self.canvas.delete("all")
            x_increment = self.width / float(self.max_data_points - 1)
            y_increment = self.height / float(self.max_value)
            timestamp = time.strftime("%M:%S", time.localtime())
            self.timestamps.append(timestamp)
            for i in range(1, len(self.data)):
                x1 = (i - 1) * x_increment
                y1 = self.height - (self.data[i - 1] * y_increment)
                x2 = i * x_increment
                y2 = self.height - (self.data[i] * y_increment)
                self.canvas.create_line(x1, y1, x2, y2, fill="blue")
                if i % 4 == 0:
                    self.canvas.create_text(x1, self.height + 5, anchor=tk.SE, text=self.timestamps[i])

    chart_width = 810
    chart_height = 610
    canvas = tk.Canvas(root, width=chart_width, height=chart_height, bg="white")
    canvas.pack()

    temperature_chart = TemperatureChart(canvas, chart_width, chart_height)


    x_caption = Label(root, text="Timestamp")
    x_caption.pack()
    l1 = Label(root, text="")
    l1.pack()
    lower_threshold_label = Label(root, text="Lower Threshold: ")
    lower_threshold_label.pack()
    lower_threshold_value = StringVar()
    lower_threshold_value.set(n1)
    
    upper_threshold_label = Label(root, text="Upper Threshold: ")
    upper_threshold_label.pack()
    upper_threshold_value = StringVar()
    upper_threshold_value.set(n2)

    
    def update_temperature_display():
        nonlocal heating_system_status
        temperature_value.set(f"{temperature} °C")
        heating_status_label.config(text="Heating System: {}".format(heating_system_status))
        temperature_chart.add_data(temperature)
        temperature_chart.update()
        
        n1 = float(config["TEMPERATURE_THRESHOLDS"]["lower_threshold"])
        n2 = float(config["TEMPERATURE_THRESHOLDS"]["upper_threshold"])
        lower_threshold_label.config(text=f"Lower Threshold: {n1} °C")
        upper_threshold_label.config(text=f"Upper Threshold: {n2} °C")

        if temperature < n1:
            # Turn on the heating system
            heating_system_status = "ON"
        elif temperature > n2:
        # Turn off the heating system
            heating_system_status = "OFF"
        root.after(1500, update_temperature_display)  
    
    update_temperature_display() 
    
    
    root.mainloop()

@app.route("/update-thresholds", methods=["POST"])
def update_thresholds():
    global n1, n2, heating
    n1 = int(request.form["lower_threshold"])
    n2 = int(request.form["upper_threshold"])
    temp_reading = get_temp_reading()

    conn = mysql.connect()
    cursor = conn.cursor()

    
    cursor.execute("INSERT INTO room_settings (turn_on_temperature, turn_off_temperature) VALUES (%s, %s)", (str(n1), str(n2)))

    conn.commit()
    cursor.close()
    conn.close()
    update_heating_system(temp_reading)
    config["TEMPERATURE_THRESHOLDS"]["lower_threshold"] = str(n1)
    config["TEMPERATURE_THRESHOLDS"]["upper_threshold"] = str(n2)
    with open("config.ini", "w") as configfile:
        config.write(configfile)
    return jsonify({"message": "Thresholds updated successfully", "lower_threshold": n1, "upper_threshold": n2, "status": heating})

if __name__ == "__main__":
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()
    app.run()
