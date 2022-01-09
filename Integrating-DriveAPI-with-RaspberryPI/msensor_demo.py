#!/usr/bin/python
# the project is a integration of a security system with google drive API
# the project uses several small snippets of code from the internet
# notable internet resources are stackoverflow, geeksforgeeks, openCV documentation,
# raspberry pi forums, Google Drive API documentation, etc..
# notable mention also to prof.Lukasz Rojek for helping with the Google drive authentaction problem
# in the following code, the contribution of internet is noted as (1), prof.Rojek as (2),
# personal code as (3), demo code from JoyPi as (4)

import RPi.GPIO as GPIO
import time
import configparser
import cv2
import os
from multiprocessing import process
from datetime import datetime
#from pydrive.auth import GoogleAuth # comment out this for auto authentication
#from pydrive.drive import GoogleDrive # comment out this for auto authentication

from Google import Create_Service  # use this for auto authentication
from googleapiclient.http import MediaFileUpload # use this for auto authentication

# creatig a .ini file for specifying some essential information for the user
# contribution for below code from (2), (4) and (3)
cfg = configparser.ConfigParser()  # creating list object of the .ini file
cfg.read("/home/pi/Desktop/DSP-Joy-Pi/input.ini") #use the path of .ini file

# checking if all the values are in .ini file
assert "PIR" in cfg, "missing motion sensor in input.ini"
assert "CAM" in cfg, "missing camera in input.ini"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(int(cfg["PIR"]["sensor_pin"]), GPIO.IN)
GPIO.setup(int(cfg["PIR"]["buzzer_pin"]), GPIO.OUT)


# contribution for below from (3) and (4)
def beeploop():
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.HIGH)  # Start Beep
    time.sleep(0.2)  # Beep for 0.5 seconds
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.LOW)  # Stop Beep
    time.sleep(0.5)
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.HIGH)  # Start Beep
    time.sleep(0.2)  # Beep for 0.5 seconds
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.LOW)  # Stop Beep
    time.sleep(0.5)
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.HIGH)  # Start Beep
    time.sleep(0.2)  # Beep for 0.5 seconds
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.LOW)  # Stop Beep
    time.sleep(0.5)
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.HIGH)  # Start Beep
    time.sleep(0.2)  # Beep for 0.5 seconds
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.LOW)  # Stop Beep
    time.sleep(0.5)
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.HIGH)  # Start Beep
    time.sleep(0.2)  # Beep for 0.5 seconds
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.LOW)  # Stop Beep
    time.sleep(0.5)


# contribution for below from (3) and (4)
def singlebeep():
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.HIGH)  # Start Beep
    time.sleep(0.2)  # Beep for 0.5 seconds
    GPIO.output(int(cfg["PIR"]["buzzer_pin"]), GPIO.LOW)  # Stop Beep


# contribution for below from (1) and (3)
def capture_image():
    cam = cv2.VideoCapture(0)
    time.sleep(1)
    ret, frame = cam.read()
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    img_name = "frame_{}.jpg".format(current_time)
    path = '/home/pi/Desktop/DSP-Joy-Pi/security'
    intruder = cv2.imwrite(os.path.join(path, img_name), frame)
    # print("program ended..")
    print("picture captured")
    print("current_time= ", current_time)

    if not cam.isOpened():
        print("couldn't open camera")

    return intruder


# contribution for below from (1) and (3)
def record_video():
    cap = cv2.VideoCapture(0)
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'X264')  # can also use 'H264/ mp4v/x264/DIVX/XVID'
    #now = datetime.now()
    #current_time = now.strftime("%Y-%m-%d-%H:%M:%S")
    #vid_name = "Vid_{}.avi".format(current_time)  # write current date and time as file name
    record_video.count += 1
    vid_name = "vid_{}.avi".format(record_video.count)
    path = '/home/pi/Desktop/DSP-Joy-Pi/security'  # the path of the folder where file is saved
    out = cv2.VideoWriter(os.path.join(path, vid_name), fourcc, 10, (640, 480))
    start_time = time.time()
    while (int(time.time() - start_time) < int(cfg["CAM"]["video_duration"])):
        ret, frame = cap.read()
        font = cv2.FONT_HERSHEY_SIMPLEX
        origin = (5, 450)
        fontscale = 0.8
        colour = (255, 255, 255)
        thickness = 1
        cv2.putText(frame, str(datetime.now().strftime("%Y.%m.%d-%H:%M:%S")),
                    origin, font, fontscale, colour, thickness, cv2.LINE_AA)  # watermark current datetime info
        if ret == True:
            out.write(frame)
        else:
            print("failed to record!")
            break
    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
record_video.count = 0


# contribution for below from (1) and (3)
'''def UploadToDrive():
    gauth = GoogleAuth()
    print("step:1 google authorisation started")
    gauth.LocalWebserverAuth()
    print("step:2 authorisation completed!")
    drive = GoogleDrive(gauth)
    path = f"/home/pi/Desktop/DSP-Joy-Pi/security" # path of the folder were video is saved
    for x in os.listdir(path):  # select all files in security folder for upload
        # use personal drive ID and save a .json file in the same folder as the code
        f = drive.CreateFile({'parents': [{'id': '<Insert your google drive folder id here>'}]})
        f.SetContentFile(os.path.join(path, x))
        print("step:3 selected file for upload")
        f.Upload()
        print("file uploaded!")
    # f.Trash()
    # print("moved to trash!")'''

# contribution for below from (1) and (3)
def Self_Upload():
    CLIENT_SECRET_FILE = "credentials.json"
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    folder_id = '<Insert your google drive folder id here>'
    file_names = ['vid_{}.avi'.format(record_video.count)] #['Vid_{current_time}.mp4']
    mime_type = ['video/avi']
    for file_name, mime_type in zip(file_names, mime_type):
        file_metadata = {
            'name' : file_name,
            'parents' : [folder_id]
        }
        media = MediaFileUpload('./security/{0}'.format(file_name), mimetype=mime_type)
        service.files().create(
            body = file_metadata,
            media_body = media,
            fields = 'id'
        ).execute()


# contribution for below from (1) and (3)
def mein_callback(channel):
    # print("ring buzzer") # add buzzer
    singlebeep()  # buzzer sound for indicating movement
    print('Movement Detected!')
    mein_callback.count += 1
    # print(f'count={mein_callback.counter}')
    if mein_callback.count >= int(cfg["CAM"]["motion_threshold"]):
        record_video()
        time.sleep(1)
        #UploadToDrive()  # select this for testing authentication
        Self_Upload() # use this for auto authentation when device not accessible
        print("Intruder video captured and saved in security and uploaded to drive!")
        mein_callback.count = 0

mein_callback.count = 0


# contribution for below from (1) and (3)
def sense_motion():
    try:
        GPIO.add_event_detect(int(cfg["PIR"]["sensor_pin"]), GPIO.RISING, callback=mein_callback)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program ended...")
    GPIO.cleanup()


if __name__ == '__main__':
    sense_motion()

