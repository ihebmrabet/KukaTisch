import socket
import sys
import xml.etree.ElementTree as ET
import math as ma
import os
import string
import threading

import paho.mqtt.client as mqtt

import time
import numpy as np


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Bind the socket to the port
#server_address = ('172.31.1.150', 50040)
server_address = ('192.168.1.150', 50040)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)



def idi(tex):
    posi = 0
    while True:
        newValue = input(tex+' = ')
        print(type(newValue))
        try:
            posi = int(newValue)
            break
        except:
            pass
    return posi



def fun():
	pass



def on_message(client, userdata, msg):
    global art
    global Fra
    print("received message")
    print(msg.topic+" "+str(msg.payload))
    if(msg.topic == "comRobot/plc/currProg"):
        txt = msg.payload
        t = [char for char in txt]
        Fra = [int(s) for s in t if s.isdigit()][0]
        art = None
    elif(msg.topic == "comRobot/plc/currwood"):
        art = int(msg.payload)
        Fra = None

def comMQTT():
    global client
    broker_address="mqtt.eclipseprojects.io"
    client = mqtt.Client("Robot") #create new instance
    client.connect(broker_address) #connect to broker
    print("started mqtt")
    while True:
        client.loop_start()
        client.subscribe("comRobot/plc/currProg")
        client.subscribe("comRobot/plc/currwood")
        client.on_message = on_message
        time.sleep(30)






def checkChangeValue():
    global run
    global outp
    global inp
    global sent
    global Pos
    global xml
    global Fra
    global art
    Fra = None
    art = None
    worked = None
    ok = False

    while True :
        while inp[0] == None:
            fun()
        if (inp[0] == 1) and (outp[1] != 9) :
            run = False
            client.publish("comRobot/robot/state", "0")
            while (art==None):
                fun()
            client.publish("comRobot/robot/state", "1")
            #art = idi('ART')
            print(art)
            outp[0] = art
            outp[1] = 9
            outp[2] = 9
            art = None
            ok = True
        elif (inp[0] == 2) and (inp[1] == 0) and (outp[1] == 9) :
            run = False
            client.publish("comRobot/robot/answer", "Woodgrip")
            while (fra==None):
                fun()
            print(Fra)
            #Fra = idi('Fra')
            outp[1] = Fra
            outp[2] = 9
            ok = True
            Fra = None
            print(inp[3])
        elif (inp[0] == 2) and (inp[1] == 0) and (outp[1] != 9) and (inp[3] == 1) and (worked != 5):
            print(inp[3])
            sent = False
            print(worked)
            print(inp[2])
            while worked == inp[2] :
                if inp[3] != 1:
                    sent = False
                fun()
            print(inp[2])
            run = False
            #Work(inp[2])
            txt = "S"+str(inp[2])+"f"
            client.publish("comRobot/robot/answer", txt)
            while (Fra==None):
                fun()
            worked = Fra
            #worked = idi('Done '+ str(inp[2]))
            outp[2] = worked
            Fra = None
            ok = True
        elif (inp[0] == 2) and (inp[1] == 1):
            print('Finished Fra')
            while inp[1] == 1 :
                fun()
            print('Finished Rest')
            client.publish("comRobot/robot/state", "0")
            run = False
            while (art==None):
                fun()
            print(art)
            client.publish("comRobot/robot/state", "1")
            #art = idi('ART')
            outp[0] = art
            outp[1] = 9
            outp[2] = 9
            art = None
            worked = None
            inp[2] = None
            ok = True

        xml='<Robot>' \
                 '<Data>' \
                     '<ARTH>' + str(outp[0]) + '</ARTH>' \
                     '<ARTF>' + str(outp[1]) + '</ARTF>' \
                     '<FRASTARTF>' + str(outp[2]) + '</FRASTARTF>' \
                 '</Data>' \
            '</Robot>'
        if ok :
            sent = False
            #print(xml)
            ok = False
        run = True
        if inp[3] != 1:
            ok = True








# Listen for incoming connections
sock.listen(1)
global run
global inp
global outp
global sent
global kkf

kkf = False

sent = False
inp = [None,None,None,None]
outp = [None,None,None]

Grr = None
Frastt = None
Recc = None

run = True
St = False
threading.Thread(target=comMQTT).start()
threading.Thread(target=checkChangeValue).start()
#threading.Thread(target=wcontroller).start()

while True:
    # Wait for a connection
    print('waiting for a connection', file=sys.stderr)
    connection, client_address = sock.accept()
    connection.setblocking(False)
    try:
        print('connection from', client_address, file=sys.stderr)

        # Receive the data in small chunks and retransmit it
        while True:
            while run:
                try:

                    if St and not sent :
                        connection.send(bytearray(xml,'utf-8'))
                        print('sent data "%s"' , xml)
                        sent = True
                    #if run == True :
                        #print('new xml = ',xml)
                        #run = False
                    data = connection.recv(1024)
                    print('received "%s"' % data, file=sys.stderr)
                    if data and (data.decode("utf-8").find("<Robot") != -1 and data.decode("utf-8").find("/Robot>") != -1):
                        data = data.decode("utf-8")[(data.decode("utf-8").find("<Robot")):].encode("utf-8")
                        data = data.decode("utf-8")[:(data.decode("utf-8").find("/Robot")+7)].encode("utf-8")
                        xmlroot = ET.fromstring(data)
                        try:
                            Stt = int(float(xmlroot.find('Data').find('Act').find('St').text))
                        except:
                            pass
                        try:
                            Grr = int(float(xmlroot.find('Data').find('Act').find('Gr').text))
                        except:
                            pass
                        try:
                            Frastt = int(float(xmlroot.find('Data').find('Act').find('FRASTART').text))
                        except:
                            pass
                        try:
                            Recc = int(float(xmlroot.find('Data').find('Act').find('REC').text))
                        except:
                            Recc = 0
                            pass
                        inp = [Stt,Grr,Frastt,Recc]

                        if Stt == 1:
                            St = True
                            run = False

                    else:
                        print('no more data from', client_address, file=sys.stderr)
                        break
                except:
                    pass

    finally:
        # Clean up the connection
        connection.close()
