import tkinter as tk
import customtkinter as ck
#import pandas as pd
import numpy as np

import mediapipe as mp
import cv2
from PIL import Image, ImageTk

#from landmarks import landmarks

window = tk.Tk()
window.geometry("520x700")
window.title("move_app")
ck.set_appearance_mode("system")  #dark light
ck.set_default_color_theme("green")
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)
fg_colour = '#5bbbcb' #(91, 187, 203)
fg_color_reset = '#637d9e'

checkbox_frame = ck.CTkFrame(window)
checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nwe")
classLabel = ck.CTkLabel(checkbox_frame, font=("Arial", 20), text='STAGE', text_color="black")
#height=40, width=120 padx=10
classLabel.grid(row=0, column=0, padx=10, pady=(10, 0)) #sticky="w"
counterLabel = ck.CTkLabel(checkbox_frame, font=("Arial", 20), text='REPS', text_color="black")
counterLabel.grid(row=0, column=1, padx=10, pady=(10, 0))
#corner_radius
classBox = ck.CTkLabel(checkbox_frame, height=40, width=120, font=("Arial", 20), text='0', text_color="white", fg_color=fg_colour, corner_radius=7)
classBox.grid(row=1, column=0, padx=10, pady=(10, 0)) #sticky="w"
counterBox = ck.CTkLabel(checkbox_frame, height=40, width=120, font=("Arial", 20), text='0', text_color="white", fg_color=fg_colour, corner_radius=7)
counterBox.grid(row=1, column=1, padx=10, pady=(10, 0))

lower_frame = ck.CTkFrame(window)
lower_frame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="swe")
maxLabel = ck.CTkLabel(lower_frame, font=("Arial", 15), text='MAX ANGLE', text_color="black", padx=10)
maxLabel.grid(row=0, column=1, padx=5, pady=(10, 0), sticky="w")
minLabel = ck.CTkLabel(lower_frame, font=("Arial", 15), text='MIN ANGLE',  text_color="black", padx=10)
minLabel.grid(row=0, column=2, padx=5, pady=(10, 0), sticky="w") #font=("Arial", 20)
maxBox = ck.CTkLabel(lower_frame, height=40, width=100, font=("Arial", 15), text='0', text_color="white", fg_color=fg_colour, corner_radius=7)
maxBox.grid(row=1, column=1, padx=5, pady=(10, 0), sticky="w")
minBox = ck.CTkLabel(lower_frame, height=40, width=100, font=("Arial", 15),text='0', text_color="white", fg_color=fg_colour, corner_radius=7)
minBox.grid(row=1, column=2, padx=5, pady=(10, 0), sticky="w")


def change_side():
    global main_body_side, add_body_side
    main_body_side, add_body_side = add_body_side, main_body_side
    button_side.configure(text=main_body_side)


main_body_side = 'RIGHT'
add_body_side = 'LEFT'
button_side = ck.CTkButton(lower_frame, text=main_body_side, command=change_side, width=120, font=("Arial", 20), text_color="white", fg_color=fg_color_reset)
button_side.grid(row=0, column=3, padx=5, pady=10, sticky="w", rowspan=2) #pady=(10, 0)

warnBox = ck.CTkLabel(checkbox_frame, font=("Arial", 20), height=40, width=200, text='Camera Aligned', text_color="white", fg_color="green", corner_radius=7)
warnBox.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="w",  rowspan=2)


def reset_counter():
    global counter, max_angle, min_angle
    counter = 0
    max_angle = 0
    min_angle = 180


button = ck.CTkButton(lower_frame, text='RESET', command=reset_counter, width=120, font=("Arial", 20), text_color="white", fg_color=fg_color_reset)
button.grid(row=0, column=0, padx=5, pady=10, sticky="w", rowspan=2) #pady=(10, 0)


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End
    ba = a - b
    bc = c - b
    angle_rad = np.arccos(np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc)))
    # radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(angle_rad * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


def calculate_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


frame = tk.Frame(window, height=480, width=480)
frame.grid(row=1, column=0, padx=10, pady=(10, 0)) #sticky="n"
#frame.place(x=10, y=90)
labelmain = tk.Label(frame)
labelmain.grid(row=1, column=0, padx=10, pady=(10, 0)) #.place(x=0, y=0)

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_tracking_confidence=0.5, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

current_stage = ''
counter = 0
min_angle = 180
max_angle = 0
#align_camera = True
#main_body_side = 'RIGHT'
#add_body_side = 'LEFT'   #LEFT_HIP


def detect():
    global current_stage
    global counter, min_angle, max_angle
    global align_camera
    global main_body_side, add_body_side

    ret, fig = cap.read()
    image = cv2.cvtColor(fig, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    try:
        landmarks = results.pose_landmarks.landmark
        #print(*mp_pose.PoseLandmark)
        hip_r = [landmarks[mp_pose.PoseLandmark[main_body_side+'_HIP'].value].x,
                      landmarks[mp_pose.PoseLandmark[main_body_side+'_HIP'].value].y]
        hip_l = [landmarks[mp_pose.PoseLandmark[add_body_side+'_HIP'].value].x,
                    landmarks[mp_pose.PoseLandmark[add_body_side+'_HIP'].value].y]
        knee = [landmarks[mp_pose.PoseLandmark[main_body_side+'_KNEE'].value].x, landmarks[mp_pose.PoseLandmark[main_body_side+'_KNEE'].value].y]
        ankle = [landmarks[mp_pose.PoseLandmark[main_body_side+'_ANKLE'].value].x, landmarks[mp_pose.PoseLandmark[main_body_side+'_ANKLE'].value].y]

        hip_r = (np.multiply(hip_r, [640, 480])).astype(int)  #[1280, 720]
        hip_l = (np.multiply(hip_l, [640, 480])).astype(int)
        knee = (np.multiply(knee, [640, 480])).astype(int)
        ankle = (np.multiply(ankle, [640, 480])).astype(int)

        visibility_hip = landmarks[mp_pose.PoseLandmark[main_body_side+'_HIP'].value].visibility > 0.5
        visibility_knee = landmarks[mp_pose.PoseLandmark[main_body_side+'_KNEE'].value].visibility > 0.5
        visibility_ankle = landmarks[mp_pose.PoseLandmark[main_body_side+'_ANKLE'].value].visibility > 0.5
        visibility_leg = visibility_hip * visibility_knee * visibility_ankle

        # Calculate offset
        dist = calculate_distance(hip_l, hip_r)
        if (dist > 30) or not visibility_leg:
            warnBox.configure(text='Align camera', fg_color='red')
        else:
            # Calculate angle
            warnBox.configure(text='Camera Aligned', fg_color='green')
            angle = calculate_angle(hip_r, knee, ankle)

            if angle > 160:
                current_stage = "up"
            if angle < 100 and current_stage == 'up':
                current_stage = "down"
                counter += 1
            max_angle = max(max_angle, angle)
            min_angle = min(min_angle, angle)

    except Exception as e:
        #pass
        print(e)

    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(0, 135, 137), thickness=3, circle_radius=3),
                              mp_drawing.DrawingSpec(color=(99, 125, 158), thickness=3, circle_radius=5))

    #img = image[:, :460, :]
    img = image
    imgarr = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(imgarr)
    labelmain.imgtk = imgtk
    labelmain.configure(image=imgtk)
    labelmain.after(10, detect)

    counterBox.configure(text=counter)
    classBox.configure(text=current_stage)
    maxBox.configure(text="%.2f" % max_angle)
    minBox.configure(text="%.2f" % min_angle)


detect()
#window.update()
window.mainloop()
#pyinstaller --name 'ACL_squats' --windowed --icon 'icon.ico' --paths=/Users/valeriia/miniconda3/lib/python3.10/site-packages  move_app.py
           #   --add-data='./strong_beat.wav:.'  --paths=[myLocalDir]/PycharmProjects/[myProject]/venv/Lib/site-packages
#pyinstaller my_script.spec

#<key>NSCameraUsageDescription</key>
#<string>$(PRODUCT_NAME) uses Cameras</string>