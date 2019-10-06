from tkinter import *
import threading
import time
import calendar
from bokeh.plotting import figure,show
import bokeh
import serial.tools.list_ports
master = Tk()

#Setup available serial ports

listboxports = serial.tools.list_ports.comports()
lb1 = Listbox(master)
index=0
for x in listboxports:
    lb1.insert(index,str(x.device))
    index=index+1
lb1.pack()
ports = []
index=0
for x in listboxports:
    ports.append(x.device)
    index=index+1
ser = serial.Serial()
ser.baudrate = 19200

ser.timeout = .1
cameraFound = False

#Look through the possible Bauds just in case it was changed

def scanBauds():
    bauds = [4800,9600,19200,38400,57600,57600,115200,230400]
    for x in bauds:
        ser.baudrate=x
        ser.flushInput()
        ser.close()
        ser.port=ports[lb1.curselection()[0]]
        ser.open()
        ser.write(str.encode('@253PR1?;FF'))
        response = ser.read_until(";FF")
        print(str(x) + ": " + str(response))
        if ("ACK" in str(response)):
            print("Sensor Found!")
            global cameraFound
            cameraFound=True
            return
    cameraFound=False
    print("Sensor not found")
    ser.baudrate=19200


#Begin Multithreading

def beginLogging():
    print("logging")
    if __name__ == "__main__":
        t1 = threading.Thread(target=logging)
        t1.start()

        t1.join()
    logging()

#Logging loop

def logging():
    if (not cameraFound):
        print("No Sensor attached, use Test Sensor function")
        return
    temps=[]
    x=[]
    countnumber = 0
    startTime = calendar.timegm(time.gmtime())
    print("Log started at +" + str(startTime))
    while True:
        try:
            ser.write(str.encode('@253PR1?;FF'))
            response = ser.read_until(";FF")
            response = str(response)
            tempIndex = response.index("ACK")
            response = response[tempIndex+3:tempIndex+10]
            print(response)
            response = float(response)
            temps.append(response)

            x.append(calendar.timegm(time.gmtime())-startTime)

            if (countnumber%10 is 0 ):
                bokeh.plotting.output_file("Output.html", "Bokeh Plot", "inline")
                p = figure(title="Pressure (Torr)", x_axis_label='Time (sec)', y_axis_label='Pressure (Torr)',
                           y_axis_type="log")
                p.line(x, temps, line_width=2)
                show(p)
            countnumber=countnumber+1
            time.sleep(.1)
        except:
            print("Error reading temp for log, trying again")
            time.sleep(3)

def testCamera():
    ser.close()
    ser.port = ports[lb1.curselection()[0]]
    ser.open()
    ser.write(str.encode('@253PR1?;FF'))
    response = ser.read_until(';FF')
    print("Response: " + str(response))
    if ("ACK" in str(response)):
        print("Sensor found!")
        global cameraFound
        cameraFound = True
    else:
        cameraFound = False
    ser.flush()

#Create the window for the interface

t = Button(master, text="Test Sensor", command=testCamera)
t.pack()
b = Button(master, text="Scan Bauds", command=scanBauds)
b.pack()
s = Button(master, text="Begin Pressure Logging", command=beginLogging)
s.pack()
mainloop()