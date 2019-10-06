import serial
from tkinter import *
import threading
import time
from bokeh.plotting import figure,show
import calendar
master = Tk()


ser = serial.Serial()
ser.baudrate = 115200
ser.port='/dev/cu.SLAB_USBtoUART'
ser.open()
ser.timeout = .1
cameraFound = False
def scanBauds():
    bauds = [9600,19200,28800,38400,57600,115200,230400,460800,921600]
    for x in bauds:
        ser.baudrate=x
        ser.flushInput()
        ser.close()
        ser.open()
        ser.write(str.encode('temp rd 0\r\n'))
        response = ser.read_until("OK\r\n")
        print(str(x) + ": " + str(response))
        if ("temp" in str(response)):
            print("Camera Found!")
            global cameraFound
            cameraFound=True
            return
    cameraFound=False
    print("not found")

def beginLogging():
    print("Log Started")
    if (__name__ == "__main__"):
        log=threading.Thread(target=logging)
        log.start()

def beginConsoleInput():
    if (__name__ == "__main__"):
        console=threading.Thread(target=readInput)
        console.start()

def readInput():
    print("Console Input Enabled")
    while True:
        command = input()
        if (not command is "" or not command is "\n" or not command is "\r"):
            ser.write(str.encode(command + "\r\n"))
            print(ser.read_until("OK\r\n"))


def logging():
    if (not cameraFound):
        print("No camera attached, use \"test camera\" button")
        return
    temps=[]
    x=[]
    countnumber = 0
    startTime = calendar.timegm(time.gmtime())
    setx = []
    sety = []
    while True:
        #try:
            ser.write(str.encode('temp rd 0\r\n'))
            response = ser.read_until("OK\r\n")
            response = str(response)
            tempIndex = response.index("0:")
            response = response[tempIndex+4:tempIndex+8]

            response = float(response)
            sety.append(response)
            setx.append(calendar.timegm(time.gmtime())-startTime)
            if (len(setx) is 4):
                total = 0
                for i in sety:
                    total = total+i
                total=total/len(setx)
                temps.append(total)
                total = 0
                for i in setx:
                    total = total+i
                total=total/len(setx)
                x.append(total)
                if (len(temps) % 10 is 0):
                    p = figure(title="Camera Temperature", x_axis_label='Time (sec)', y_axis_label='Temperature (C)')
                    p.line(x, temps, line_width=2)
                    show(p)
                setx = []
                sety = []
            countnumber=countnumber+1
            time.sleep(1)
        #except:
            #print("Error reading temp for log, trying again")
            #time.sleep(3)

def testCamera():
    ser.write(str.encode('temp rd 0\r\n'))
    response = ser.read_until('OK\r\n')
    print("Response: " + str(response))
    if ("Temp" in str(response)):
        print("Camera found!")
        global cameraFound
        cameraFound = True
        return
    else:
        print("No camera found")
        cameraFound = False
    ser.flush()

def debugCamera():
    if (not cameraFound):
        print("Scanning for connection...")
        testCamera()
        if (cameraFound):
            debugCamera()

    else:
        print("Attempting to enable analog output...")
        ser.write(str.encode('av power 1\r\n'))
        time.sleep(1)


t = Button(master, text="Test Camera", command=testCamera)
t.pack()
b = Button(master, text="Scan Bauds", command=scanBauds)
b.pack()
s = Button(master, text="Begin Temperature Logging", command=beginLogging)
s.pack()
d = Button(master, text="Debug Camera", command=debugCamera)
d.pack()
c = Button(master, text="Begin Console Input", command=beginConsoleInput)
c.pack()
mainloop()