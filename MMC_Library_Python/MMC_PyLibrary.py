import serial
import serial.tools.list_ports
import socket
from socket import *

scon = ""
econ = ""


def openComPortMMC(port):
    COMport = port
    global scon
    global ser
    try:
        ser = serial.Serial(COMport, 38400, bytesize=serial.EIGHTBITS, timeout=0.020, parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE)
        scon = 'Serial'
        # print(f"Connected to {COMport}")
        return True
    except:
        # print("Failed to Connect")
        return False


serverName = "192.168.0.20"
serverPort = 5000


def connectEthMMC(serverName, serverPort):
    global econ
    global clientSocket
    global cnt_ethflag
    try:
        serverPort = int(serverPort)
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        cnt_ethflag = True
        econ = 'Ethernet'
        # print("Connected Successfully though Ethernet")
        return True
    except:
        # print("Not able to make Connection through Ethernet")
        return False


def closeConnectionMMC():
    global scon
    global econ
    try:
        if scon == 'Serial':
            ser.close()
            # print("Disconnected Serial Connection")
            scon = ''
            return True

        if econ == 'Ethernet':
            clientSocket.close()
            # print("Disconnected Parallel Connection")
            econ = ''
            return True

    except:
        # print("Not Connected so cannot disconnect")
        return False


def pollValues(axis, command):
    global scon, econ
    ser.reset_input_buffer()
    sendCommand = str(axis) + command + "?"
    if scon == 'Serial':
        sendCommand = str(sendCommand) + "\r"
        ser.write(str(sendCommand).upper().encode())
        response = ""
        while True:
            checkResponse = ser.read(1).decode('utf-8')
            if checkResponse == "":
                break
            else:
                response = response + checkResponse
        
        tekdi = response.replace("#", "")
        ser.reset_input_buffer()
        if tekdi == "":
            print("No Response or Invalid")
            return False
        else:
            return tekdi

    elif (econ == 'Ethernet') & (scon == ''):
        ethCommand = str(sendCommand) + "\r"
        clientSocket.send(ethCommand.upper().encode())
        response = ""
        response1 = ""
        clientSocket.settimeout(1)
        while True:
            try:
                response1 = clientSocket.recv(2048)
            except:
                return "No response or Invalid Command or Socket timeout or Axis changed"

            if response1 == "":
                break
            else:
                response = response1.decode('utf-8')
                break
        tekdi = response.replace("#", "")
        # print(tekdi)
        return response.replace("#", "")
    else:
        # print("Connection not done yet")
        return False


def writeCommandToMMC(axis, command):
    sendCommand = str(axis) + command
    global scon, econ
    if scon == "Serial":
        sendCommand = str(sendCommand) + "\r"
        ser.reset_output_buffer()
        ser.write(str(sendCommand).upper().encode())
        return True
    elif (econ == 'Ethernet') & (scon == ''):
        ethCommand = str(sendCommand) + "\r"
        clientSocket.send(ethCommand.upper().encode())
        return True
    else:
        # print("Connection not done yet")
        return False
