import serial
import serial.tools.list_ports
from serial import SerialException
from socket import *
import time
import threading


class UdpReader:

    def __init__(self, ip):
        self.address = (ip, 8888)
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.settimeout(1)
        self.serialIn = 'ABCDEFG'


    # Returns list of all accessible serial ports
    def getPorts(self):
        portData = serial.tools.list_ports.comports()
        print(f"Got Ports {portData}")
        return portData

    # Returns COM port of Arduino if detected by computer. User for switchbox
    def findArduino(self, portsFound):
        numConnections = len(portsFound)
        print("Find arduino Called")
        for i in range(0, numConnections):
            if ('Uno' in str(portsFound[i]) or 'Nano' in str(portsFound[i]) or 'CH340' in str(portsFound[i])):
                print(f"Found {portsFound[i]}")
                return str(portsFound[i])
            if ('USB Serial Device' in str(portsFound[i])):
                print(f"Found USB Serial Device {portsFound[i]}")
                return str(portsFound[i])
            else:
                print(f"Found another device {portsFound[i]}")
        return None

    def getData(self, requestStr):
        data = requestStr.encode('utf-8')
        print('Sending: ', data)
        self.sock.sendto(data, self.address)

        try:
            rec_data, addr = self.sock.recvfrom(2048)
            return rec_data
        except Exception as e:
            print('[getdata] ', e)
            return None
            pass


    def conv(self, str):
        return str[2:len(str) - 5]

    def serialHandler(self):

        status = self.findArduino(self.getPorts())  # Gets the Name of the CU (USB Serial Device)
        nano = serial.Serial(status.split()[0], 115200)

        while True:
            nano.flush()
            line = self.conv(str(nano.readline()))
            serialIn = line
            self.serialIn = serialIn.strip()


if __name__ == '__main__':
    udpReader = UdpReader()

    # serialIn = "ABCDEF"

    # ACTION HANDLER THREAD (checks for startup button press)
    thread = threading.Thread(target=udpReader.serialHandler)
    thread.start()


    while True:

        try:
            print(udpReader.serialIn)

            data = udpReader.getData(f"tc;sAll;{udpReader.serialIn};")
            if (data is not None):
                data = str(data, encoding='utf-8')
                tc, sAll, sol, *extra = data.split(';')

                print("TC: ", tc)
                print("Solenoid: ", sAll)
                """print("RTT: ", time.time_ns() - last_actuation)
                last_actuation = time.time_ns()"""
        except:
            print("fucked")
