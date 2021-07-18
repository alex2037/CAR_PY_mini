from XInput import *

import serial
import struct


ser = serial.Serial('COM5', 57600)


speed = 0.0
steer = 0.0
camX = 0.0
camY = 0.0
CRC = 0.0
TURBO = 25


# CONTROL by two sticks and NO letter_button - 0..250 (TURBO = 25), A - 0..500(TURBO = 50), Y - 0..1000(TURBO = 100)
# Create the handler and set the events functions
class MyHandler(EventHandler):

    def process_button_event(self, event):
        global TURBO
        if event.button == "LEFT_THUMB":
            print()
        elif event.button == "RIGHT_THUMB":
            print()
        elif event.button == "LEFT_SHOULDER":
            print()
        elif event.button == "RIGHT_SHOULDER":
            print()
        elif event.button == "BACK":
            print()
        elif event.button == "START":
            print()
        elif event.button == "DPAD_LEFT":
            print()
        elif event.button == "DPAD_RIGHT":
            print()
        elif event.button == "DPAD_UP":
            print()
        elif event.button == "DPAD_DOWN":
            print()
        elif event.button == "A":
            if (TURBO == 50):
                TURBO = 25
            else:
                TURBO = 50
        elif event.button == "B":
            print()
        elif event.button == "Y":
            if (TURBO == 100):
                TURBO = 25
            else:
                TURBO = 100
        elif event.button == "X":
            print()

    def process_stick_event(self, event):
        global steer
        global camX
        global camY
        if event.stick == LEFT:
            steer = event.x
            # print(event.x)
            # print(event.y)
        elif event.stick == RIGHT:
            camX = event.x
            camY = event.y

    def process_trigger_event(self, event):
        global speed
        if event.trigger == LEFT:
            speed = -event.value
        elif event.trigger == RIGHT:
            speed = event.value

    def process_connection_event(self, event):
        if event.type == EVENT_CONNECTED:
            print()
        elif event.type == EVENT_DISCONNECTED:
            print()
        else:
            print("Unrecognized controller event type")


if __name__ == "__main__":
    handler = MyHandler(0,1,2,3)  # initialize handler object



    thread = GamepadThread(handler)  # initialize controller thread

    while True:
        speed_send = speed * 10 * TURBO
        steer_send = steer * 10 * TURBO
        camX_send = camX * 1000
        camY_send = camY * 1000
        array = bytearray(struct.pack("h", int(speed_send)))                #-1000 ... 1000
        array.extend(bytearray(struct.pack("h", int(steer_send))))          #-1000 ... 1000
        array.extend(bytearray(struct.pack("h", int(camX_send))))           #-1000 ... 1000
        array.extend(bytearray(struct.pack("h", int(camY_send))))           #-1000 ... 1000
        CRC = speed_send + steer_send + camX_send + camY_send
        array.extend(bytearray(struct.pack("h", int(CRC))))                 #1...112
        print(speed_send)
        ser.write(array)
        #print(array)
        print(speed_send, "  ", steer_send, "  ", camX_send, "  ", camY_send )
        time.sleep(0.1)


    thread.stop()

    # can run other stuff here

else:
    raise ImportError("This is not a module. Import XInput only")
