from XInput import *

import serial
import struct
import serial.tools.list_ports
import threading

def connetc_COM():
    ports = list(serial.tools.list_ports.comports())
    serial_number = "D308ZXNSA"
    for p in ports:
        if serial_number == p.serial_number:
            return serial.Serial(p.device, 57600)
    print("NO DEVICE FOUND")


speed = 0.0
steer = 0.0
camX = 0.0
camY = 0.0
CRC = 0.0
TURBO = 25
TORQUE = 0

drive_X = 0.0
drive_Y = 0.0


# CONTROL by two sticks and NO letter_button - 0..250 (TURBO = 25), A - 0..500(TURBO = 50), Y - 0..1000(TURBO = 100)
# Create the handler and set the events functions
class MyHandler(EventHandler):

    def process_button_event(self, event):
        global TURBO
        global TORQUE
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
            TORQUE = TORQUE + 10
        elif event.button == "DPAD_DOWN":
            TORQUE = TORQUE - 10
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
        global steer, camX, camY, drive_X, drive_Y
        if event.stick == LEFT:
            steer = event.x
            drive_Y = event.y
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
        global TURBO
        if event.type == EVENT_CONNECTED:
            print()
        elif event.type == EVENT_DISCONNECTED:
            TURBO = 0
        else:
            print("Unrecognized controller event type")


def send_command(serial_port):
    speed_send = drive_Y * 10 * TURBO
    steer_send = camY * 10 * TURBO
    camX_send = camX * 1000
    camY_send = camY * 1000
    array = bytearray(struct.pack("h", int(steer_send)))  # -1000 ... 1000
    array.extend(bytearray(struct.pack("h", int(speed_send))))  # -1000 ... 1000
    array.extend(bytearray(struct.pack("h", int(camX_send))))  # -1000 ... 1000
    array.extend(bytearray(struct.pack("h", int(camY_send))))  # -1000 ... 1000
    CRC = speed_send + steer_send + camX_send + camY_send
    array.extend(bytearray(struct.pack("h", int(CRC))))  # 1...112
    serial_port.write(array)
    # print(array)
    # print(speed_send, "  ", steer_send, "  ", camX_send, "  ", camY_send)



def get_telemetry(serial_port):
    if (serial_port.in_waiting > 0):
        #print(serial_port.read(1))
        if (serial_port.read(1) == b'\xff'):
            if (serial_port.read(1) == b'\xff'):
                serial_byte_array = serial_port.read(32)
                T2 = struct.unpack('16h', serial_byte_array)
#0-F(orward)L(eft)T(ask) 1-FLS(peed) 2-FR(ight)T 3-FRS 4-FD(river)V(oltage)
#5-M(iddle)LT 6-MLS 7-MRT 8-MRS 9-MDV
#10-R(ear)LT 11-RLS 12-RRT 13-RRS 14-RDV
                if ((T2[0] ^ T2[1] ^ T2[2] ^ T2[3] ^ T2[4] ^ T2[5] ^ T2[6] ^ T2[7] ^ T2[8] ^ T2[9] ^ T2[
                    10] ^ T2[11] ^
                     T2[12] ^ T2[13] ^ T2[14]) == T2[15]):
                    #print(T2)
                    print('SPEED \n {FLS}          {FRS} \n {MLS}          {MRS}\n {RLS}           {RRS} '.format(FLS=T2[1],FRS=T2[3],MLS=T2[6],MRS=T2[8],RLS=T2[11],RRS=T2[13]))
                    print('VOLTAGE FRONT={FDV}          MIDDLE={MDV}          REAR={RDV}'.format(FDV=T2[4],MDV=T2[9],RDV=T2[14]))
                    print('TASKS \n {FLT}          {FRT} \n {MLT}          {MRT}\n {RLT}           {RRT}'.format(FLT=T2[0],FRT=T2[2],MLT=T2[5],MRT=T2[7],RLT=T2[10],RRT=T2[13]))

if __name__ == "__main__":
    handler = MyHandler(0, 1, 2, 3)  # initialize handler object
    ser = connetc_COM()

    data_file = open('data.csv','w')
    thread = GamepadThread(handler)  # initialize controller thread

    while True:
        send_command(ser)
        get_telemetry(ser)
        time.sleep(0.01)

    thread.stop()

    # can run other stuff here

else:
    raise ImportError("This is not a module. Import XInput only")
