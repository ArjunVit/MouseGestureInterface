import serial
import time
import pyautogui
from queue import Queue
from threading import Thread

pyautogui.FAILSAFE = False
# stop_acceleration_y = 0
# stop_acceleration_z = 0
smoothed_acceleration_y, smoothed_acceleration_z = 0, 0
def analyze_movement():
    iteration_cnt = 0
    left_double, right_double = 0, 0
    pre_acc_x, pre_acc_y, pre_acc_z, pre_left, pre_right = 10, 0, 0, 0, 0
    prev_time = time.time()
    while True:
        if stop_thread:
            break
        if not data_queue.empty():
            data = data_queue.get()
            acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, left_click, right_click = map(float, data.split(" "))
            current_time = time.time()
            time_step = current_time - prev_time
            prev_time = current_time
            if pre_acc_x - acc_x > x_threshold:
                if iteration_cnt >= 10:
                    if acc_y - pre_acc_y > y_z_threshold:
                        print("Movement: Up and left")
                        pyautogui.hotkey('alt', 'shift', 'tab')
                    elif pre_acc_y - acc_y > y_z_threshold:
                        print("Movement: Up and right")
                        pyautogui.hotkey('alt', 'tab')
                    elif acc_z - pre_acc_z > y_z_threshold:
                        print("Movement: Up and backward")
                        pyautogui.hotkey('win', 'd')
                    elif pre_acc_z - acc_z > y_z_threshold:
                        print("Movement: Up and forward")
                        pyautogui.hotkey('win', 'up')
                    else:
                        print("Movement: Only up")
                        pyautogui.hotkey('ctrl', 'alt', 'tab')
                    iteration_cnt = 0
            else:
                move_mouse_with_acceleration(acc_y, pre_acc_y, acc_z, pre_acc_z, time_step)
                if pre_left == 1 and left_click == 0:
                    if left_double <= 14:
                        print("Double Click Left")
                        pyautogui.doubleClick(button="left")
                    else:
                        print("Left")
                        pyautogui.leftClick()
                    left_double = 0
                if pre_right == 1 and right_click == 0:
                    if right_double <= 14:
                        print("Double Click Right")
                        pyautogui.doubleClick(button="right")
                    else:
                        print("Right")
                        pyautogui.rightClick()
                    right_double = 0
                iteration_cnt += 1
                left_double += 1
                right_double += 1
            pre_acc_x, pre_acc_y, pre_acc_z, pre_left, pre_right = acc_x, acc_y, acc_z, left_click, right_click

# def move_mouse_with_acceleration(dev_y, dev_z, time_step):
#     sensitivity = 50
#     move_y = dev_y * sensitivity
#     move_z = dev_z * sensitivity

#     # Calculate velocity and displacement
#     velocity_y = move_y * time_step
#     velocity_z = move_z * time_step

#     # Get current mouse position
#     current_pos = pyautogui.position()

#     # Calculate displacement
#     displacement_y = int(velocity_y)
#     displacement_z = int(velocity_z)

#     # Move the mouse based on the displacement
#     new_x = current_pos[0] + displacement_y
#     new_y = current_pos[1] + displacement_z
#     pyautogui.moveTo(new_x, new_y, duration=0)

# def move_mouse_with_acceleration(dev_y, dev_z, time_step):
#     sensitivity = 500
#     global smoothed_acceleration_y, smoothed_acceleration_z
#     smoothed_dev_y = smooth_acceleration(dev_y, smoothed_acceleration_y)
#     smoothed_dev_z = smooth_acceleration(dev_z, smoothed_acceleration_z)
#     move_y = smoothed_dev_y * sensitivity * time_step
#     move_z = smoothed_dev_z * sensitivity * time_step
#     pyautogui.moveRel(move_y, move_z)

# def smooth_acceleration(acceleration, smoothed_acceleration, smoothing_factor=0.5):
#     smoothed_acceleration = smoothed_acceleration * smoothing_factor + acceleration * (1 - smoothing_factor)
#     return smoothed_acceleration

def move_mouse_with_acceleration(acc_y, pre_acc_y, acc_z, pre_acc_z, time_step):
    sensitivity = 50
    global stop_acceleration_y, stop_acceleration_z
    dev_y = acc_y - pre_acc_y
    dev_z = acc_z - pre_acc_z
    if acc_y > pre_acc_y:
        stop_acceleration_y = -1
    elif acc_y < pre_acc_y:
        dev_y *= 1
        stop_acceleration_y = 1
    if acc_z > pre_acc_z:
        stop_acceleration_z = -1
    elif acc_z < pre_acc_z:
        dev_z *= 1
        stop_acceleration_z = 1

    move_y = dev_y * sensitivity * time_step + stop_acceleration_y * sensitivity * time_step
    # move_y = dev_y * sensitivity * time_step
    move_z = dev_z * sensitivity * time_step + stop_acceleration_z * sensitivity * time_step
    # move_z = dev_z * sensitivity * time_step
    pyautogui.moveRel(move_y, move_z)

def read_serial():
    bluetooth_port = 'COM3'
    ser = serial.Serial(bluetooth_port, 9600)
    ser.write(b'Trigger\n')
    time.sleep(1)

    while True:
        if stop_thread:
            break
        data = ser.readline().decode().strip()
        # print(data)
        if data_queue.qsize() >= 10:
            data_queue.get()
        data_queue.put(data)

if __name__ == '__main__':
    data_queue = Queue(maxsize=10)
    x_threshold = 5
    y_z_threshold = 3
    stop_thread = 0

    read_thread = Thread(target=read_serial)
    analyze_thread = Thread(target=analyze_movement)
    read_thread.start()
    analyze_thread.start()
    read_thread.join()
    analyze_thread.join()
