
import cv2
import os
import numpy as np
from mss import mss
import win32api
import serial
import time

# Constants
COM_PORT = 'COM6'
BAUD_RATE = 115200
KERNEL_SIZE = (3, 3)
DILATE_ITERATIONS = 5
THRESHOLD_VALUE = 60
THRESHOLD_MAX = 255
KEY_LEFT_MOUSE = 0x01
COLOR_LOWER_BOUND = np.array([140, 111, 160])
COLOR_UPPER_BOUND = np.array([148, 154, 194])

def clear_console():
    """Clear the console and set the color to green."""
    os.system("color 2")
    os.system("cls")

def display_welcome_message():
    """Display the welcome message."""

def display_welcome_message():
    """Display the welcome message."""
    print(" _____ _               _______ ")
    print("|_   _| |             / /____ |")
    print("  | | | |__  _   _   / /    / /")
    print("  | | | '_ \| | | | < <     \ \ ")
    print("  | | | | | | |_| |  \ \.___/ / ")
    print("  \_/ |_| |_|\__,_|   \_\____/  ")        
                                                        
def get_fov():
    """Prompt the user to input the FOV and return it as an integer."""
    while True:
        try:
            fov = int(input("FOV: "))
            if fov > 0:
                return fov
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

def get_speed():
    """Prompt the user to input the speed and return it as a float."""
    while True:
        try:
            speed = float(input("SPEED: "))
            if speed > 0:
                return speed
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def mouse_move(x):
    """Send the x-coordinate to the Arduino."""
    if x < 0:
        x += 256
    arduino.write([int(x)])

def main():
    clear_console()
    display_welcome_message()

    fov = get_fov()
    speed = get_speed()

    # Setup screenshot capture
    sct = mss()
    screenshot = sct.monitors[1]
    screenshot['left'] = int((screenshot['width'] / 2) - (fov / 2))
    screenshot['top'] = int((screenshot['height'] / 2) - (fov / 2))
    screenshot['width'] = fov
    screenshot['height'] = fov
    center = fov / 2

    # Setup Arduino connection
    try:
        global arduino
        arduino = serial.Serial(COM_PORT, BAUD_RATE)
        time.sleep(2)  # Wait for the serial connection to initialize
    except serial.SerialException as e:
        print(f"Error opening serial port {COM_PORT}: {e}")
        return

    clear_console()
    print("  _                      _       ")
    print(" (_)                    | |      ")
    print("  _       ___  _____  __| |      ")
    print(" | |     / _ \(____ |/ _  |      ")
    print(" | |____| |_| / ___ ( (_| |_ _ _ ")
    print(" |_______)___/\_____|\____(_|_|_)")
                                

    kernel = np.ones(KERNEL_SIZE, np.uint8)

    try:
        while True:
            if win32api.GetAsyncKeyState(KEY_LEFT_MOUSE) < 0:
                img = np.array(sct.grab(screenshot))
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND)
                dilated = cv2.dilate(mask, kernel, iterations=DILATE_ITERATIONS)
                thresh = cv2.threshold(dilated, THRESHOLD_VALUE, THRESHOLD_MAX, cv2.THRESH_BINARY)[1]
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                if contours:
                    mouse = cv2.moments(thresh)
                    pixel = (int(mouse["m10"] / mouse["m00"]), int(mouse["m01"] / mouse["m00"]))
                    aim_pos = pixel[0] + 2
                    diff_x = int(aim_pos - center)
                    target_pos = diff_x * speed
                    mouse_move(target_pos)
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        arduino.close()

if __name__ == "__main__":
    main()
