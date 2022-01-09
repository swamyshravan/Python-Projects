#!/usr/bin/python3
import Adafruit_DHT
import configparser
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import influxdb



cfg = configparser.ConfigParser()       #creating list object of the .ini file
cfg.read("/home/pi/Desktop/DSP-Joy-Pi/config.ini")

#checking if all the values are in .ini file
assert "DHT" in cfg, "missing DHT in config.ini"
assert "Ultrasonic" in cfg, "missing  Ultrasonic in config.ini"
assert "InfluxDB" in cfg, "missing InfluxDB in config.ini"


humidity, temperature = Adafruit_DHT.read_retry(int(cfg["DHT"]["sensor"]), int(cfg["DHT"]["pin"]))

#print(humidity, temperature)

GPIO.setmode(GPIO.BOARD)
TRIG = int(cfg["Ultrasonic"]["trig"])
ECHO = int(cfg["Ultrasonic"]["echo"])
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)
time.sleep(2)  #delay for the sensor

GPIO.output(TRIG, True)
time.sleep(0.000001)
GPIO.output(TRIG, False)


while GPIO.input(ECHO) == 0:
    pulse_start = time.time()

while GPIO.input(ECHO) == 1:
    pulse_end = time.time()

dist = round((pulse_end - pulse_start) * 17150, 2)
GPIO.cleanup()

#write output into influxdb
db = influxdb.InfluxDBClient(host=cfg["InfluxDB"]["host"], port=int(cfg["InfluxDB"]["port"]),
                             username=cfg["InfluxDB"]["username"], password=cfg["InfluxDB"]["password"])

db.switch_database(cfg["InfluxDB"]["db"])

ts = datetime.now()
ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")

data = {
    "time": (ts - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "measurement" : "demo",
    "tags": {
        "name" : "Joy-Pi",
        "user" : "Shravan",
        "units" : "C,%,cm",
        "locaion" : "SRH"
    },
    "fields": {
        "temp": temperature,
        "hum": humidity,
        "dist": dist
    }
}

db.write_points([data])

print(f"ts = {ts_str}, hum={humidity} %, temp={temperature} C , distance = {dist} cm")


