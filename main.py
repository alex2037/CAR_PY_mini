from XInput import *

import serial
import struct
import serial.tools.list_ports
import threading
import csv
import time
import atexit


def connetc_COM(ser_number, baudrate):
    ports = list(serial.tools.list_ports.comports())
    serial_number = ser_number
    for p in ports:
        if serial_number == p.serial_number:
            return serial.Serial(p.device, baudrate)
    print("NO DEVICE FOUND")


speed = 0.0
steer = 0.0
camX = 0.0
camY = 0.0
CRC = 0.0

TURBO = 0

# CONTROL by two sticks and NO letter_button - 0..250 (TURBO = 25), A - 0..500(TURBO = 50), Y - 0..1000(TURBO = 100)
# Create the handler and set the events functions
class MyHandler(EventHandler):

    def process_button_event(self, event):
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
            print()
        elif event.button == "B":
            print()
        elif event.button == "Y":
            print()
        elif event.button == "X":
            print()

    def process_stick_event(self, event):
        global steer, speed, camX, camY, drive_X, drive_Y
        if event.stick == LEFT:
            speed = event.y
            steer = event.x
        elif event.stick == RIGHT:
            camX = event.x
            camY = event.y

    def process_trigger_event(self, event):
        global speed
        global TURBO
        if event.trigger == LEFT:
            print()
        elif event.trigger == RIGHT:
            TURBO = event.value

    def process_connection_event(self, event):
        global speed
        if event.type == EVENT_CONNECTED:
            print()
        elif event.type == EVENT_DISCONNECTED:
            speed = 0
        else:
            print("Unrecognized controller event type")
def send_command(serial_port):
    global speed,steer, camX, camY, TURBO

    speed_send =(-1)*(((speed+TURBO) * 500)*speed)
    steer_send =((steer+TURBO) * 500)*steer
    camX_send = camX * 1024 + 2048
    camY_send = camY * 1024 + 2048
    #camY_send = 2048
    #camX_send = 2048
    array = bytearray(struct.pack("h", int(speed_send)))  # -1000 ... 1000
    array.extend(bytearray(struct.pack("h", int(steer_send))))  # -1000 ... 1000
    array.extend(bytearray(struct.pack("h", int(camX_send))))  # -1000 ... 1000
    array.extend(bytearray(struct.pack("h", int(camY_send))))  # -1000 ... 1000
    CRC = speed_send + steer_send + camX_send + camY_send
    array.extend(bytearray(struct.pack("h", int(CRC))))  #
    serial_port.write(array)
    # print(array)
    print(speed_send, "  ", steer_send, "   ", camX_send, "   ", camY_send)
def get_telemetry(serial_port):
    if (serial_port.in_waiting > 0):
        # print(serial_port.read(1))
        if (serial_port.read(1) == b'\xff'):
            if (serial_port.read(1) == b'\xff'):
                serial_byte_array = serial_port.read(32)
                T2 = struct.unpack('16h', serial_byte_array)
                # 0-F(orward)L(eft)T(ask) 1-FLS(peed) 2-FR(ight)T 3-FRS 4-FD(river)V(oltage)
                # 5-M(iddle)LT 6-MLS 7-MRT 8-MRS 9-MDV
                # 10-R(ear)LT 11-RLS 12-RRT 13-RRS 14-RDV
                if ((T2[0] ^ T2[1] ^ T2[2] ^ T2[3] ^ T2[4] ^ T2[5] ^ T2[6] ^ T2[7] ^ T2[8] ^ T2[9] ^ T2[
                    10] ^ T2[11] ^
                     T2[12] ^ T2[13] ^ T2[14]) == T2[15]):
                    # print(T2)
                    print('SPEED \n {FLS}          {FRS} \n {MLS}          {MRS}\n {RLS}           {RRS} '.format(
                        FLS=T2[1], FRS=T2[3], MLS=T2[6], MRS=T2[8], RLS=T2[11], RRS=T2[13]))
                    print('VOLTAGE FRONT={FDV}          MIDDLE={MDV}          REAR={RDV}'.format(FDV=T2[4], MDV=T2[9],
                                                                                                 RDV=T2[14]))
                    print('TASKS \n {FLT}          {FRT} \n {MLT}          {MRT}\n {RLT}           {RRT}'.format(
                        FLT=T2[0], FRT=T2[2], MLT=T2[5], MRT=T2[7], RLT=T2[10], RRT=T2[13]))
def get_gyro(serial_port):
    if(serial_port.in_waiting > 0):
        if (serial_port.read(1) == b'\xAA'):
            if (serial_port.read(1) == b'\xAA'):
                if (serial_port.read(1) == b'\x37'):
                    if (serial_port.read(1) == b'\x70'):
                        serial_byte_array = serial_port.read(54)
                        T2 = struct.unpack('=I9f2ifH', serial_byte_array)
                        #T[0] - state word, T[1,2,3] - Axxel, T[4,5,6] -  angulare speed, T[7,8,9] - angle(Roll, Yaw, Pitch), T[10,11,12] - geo, T[13] - CRC
                        #print(f'ROLL : {T2[7]},   Yaw : {T2[8]},  Pitch : {T2[9]}')
                        print(f'Yaw : {T2[8]}')
def get_gyro_mouse(serial_port):
    if(serial_port.in_waiting > 0):
        if(serial_port.read(1) == b'\xAA'):
            if(serial_port.read(1) == b'\xAA'):
                if(serial_port.read(1) == b'\x13'):
                    if(serial_port.read(1) == b'\x4C'):
                        serial_byte_array = serial_port.read(12)
                        print(serial_byte_array)
                        #T2 = struct.unpack('3f', serial_byte_array)
                        #print(f'Yaw: {T2[0]}')
def thread_log(serial_port, writer):
        if (serial_port.in_waiting > 0):
            if (serial_port.read(1) == b'\xFF'):
                if (serial_port.read(1) == b'\xFF'):
                    serial_byte_array = serial_port.read(28)
                    T2 = struct.unpack('=I4h4f',serial_byte_array)
                    writer.writerow(T2)
                    print(T2)

def Exit_func(file):
    file.close()


if __name__ == "__main__":

    # INIT
    handler = MyHandler(0, 1, 2, 3)  # initialize Xbox controller handler object
    ser_holybro = connetc_COM('D308ZXNSA', 57600)
    #ser_bolid_rs232 = connetc_COM('R4841986051', 460800)
    #ser_bolid_rs485 = connetc_COM('Q6949935051', 115200)
    # ser_r2d2 = connetc_COM('FT2N0AMEA',921600)

    #data_file = open('data.csv', 'w')
    #writer = csv.writer(data_file)


    thread = GamepadThread(handler)  # initialize controller thread

    #atexit.register(Exit_func, data_file)

    while True:
        send_command(ser_holybro)



        time.sleep(0.1)


    thread.stop()

    # can run other stuff here

else:
    raise ImportError("This is not a module. Import XInput only")
