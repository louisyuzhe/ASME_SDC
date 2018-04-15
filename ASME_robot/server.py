from PyQt5.QtCore import QCoreApplication, QTimer
from arduino import Arduino
from interface import *
import pygame
from distance_sensor import *
from PID import PID
import RPi.GPIO as GPIO
from time import sleep

gear = [20, 40, 60, 80, 100]
gearIndex = 0
flag = 0
arduino = Arduino("/dev/ttyS0")
positioning = False
stillAlive = False
timer = QTimer()
xboxTimer = QTimer()
lastTurn = 0
lastDrive = 0

distanceSensorsTimer = QTimer()
distanceSensors = None
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#VEX Servo Motor pinout
GPIO.setup(36,GPIO.OUT)
q = GPIO.PWM(36, 75)
q.start(0)

#Servo motor pinout
GPIO.setup(12,GPIO.OUT)
p = GPIO.PWM(12, 40)
p.start(0)

#Claw's actuator
GPIO.setup(33, GPIO.OUT)
r = GPIO.PWM(33 ,100)
r.start(0)

#Linear Actuator pinout
Motor1A = 11    #Relay
Motor1B = 35    #Relay
GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)

def gotManualMessageSplot(message):
    if arduino.writeDirectly(message) is False:
        print("Manual control fail: ", MESAGE_STRUCT.unpack(message))
    else:
        print("Manual control: ", MESAGE_STRUCT.unpack(message))

def gotSensorMessageSplot(decodedMessage):
    print("slot sensor ", decodedMessage)

def controllerDisconnectedSlot():

    arduino.stop()
    print("stop arduino")
    global timer
    timer.stop()
    print("stop timer")

def controllerConnectedSlot():
    global timer
    timer.start(500)

def haveHeardFromControllerSlot():
    global stillAlive
    if stillAlive:
        stillAlive = False
    else:
        arduino.stop()
        print("lost controller")


def initXbox360():
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.joystick.init()
    pygame.display.set_mode((1, 1))
    #pygame.display.set_mode((1,1), pygame.HWSURFACE | pygame.DOUBLEBUF)
    clock = pygame.time.Clock()
    clock.tick(60)  # how fast it updates
    joytickCount = pygame.joystick.get_count()
    if joytickCount < 1:
        pygame.joystick.quit()
        return False
    joysticks = []
    for i in range(0, joytickCount):
        joysticks.append(pygame.joystick.Joystick(i))
        joysticks[-1].init()
        print("Detected joystick '", joysticks[-1].get_name(), "'")
    return True

def loopXboxRPI():
    "Opens a window and prints events to the terminal. Closes on ESC or QUIT."
    global lastTurn, lastDrive, flag
    for event in pygame.event.get():
        #print(event)
        # KEPT BC ITS A WAY TO STOP PROGRAM
        if event.type == pygame.QUIT:
            print("Received event 'Quit', exiting.")
            #pygame.display.quit()
            return
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            print("Escape key pressed, exiting.")
            pygame.display.quit()
            return
        elif event.type == pygame.JOYAXISMOTION:
            # for left analog stick; forward and backward motion -- full speed
            # for left analog stick; forward and backward motion -- full speed
            #print("axis", event.axis, "value", event.value)
            if event.axis == 1 or event.axis == 3:
                #print("axis 1 and  3")
                pass
            else:
                if event.axis == 0:  # Left joystick
                    lastTurn = int(100 * event.value)
                    if lastTurn < 12 and lastTurn > -22:
                        lastTurn = 0
                elif event.axis == 4:  # Right joystick
                    lastDrive = -int(100 * event.value)
                    if abs(lastDrive) < 12:
                        lastDrive = 0
                elif event.axis == 2:  # trigger Left
                    print("Yuzhe Hey")
                elif event.axis == 5:  # Trigger Rigth
                    print("Hello Louis")
                else:
                    pass
            print(lastDrive, lastTurn)
            #arduino.drive(lastDrive, lastTurn)
            arduino.drive(lastDrive, 0)
            lastTurn = int(lastTurn/2)
            arduino.turn(0, lastTurn)

        elif event.type == pygame.JOYBUTTONDOWN:
            # print ("Joystick '",joysticks[event.joy].get_name(),"' button",event.button,"pressed.")
            if event.button == 0: #A
                print("claw is moving")
                r.ChangeDutyCycle(7.5)
                sleep(4)
                r.ChangeDutyCycle(12.5)
                sleep(4)
                pass
            if event.button == 1: #B
                print ("Reload Actuator")
                GPIO.output(Motor1A, GPIO.HIGH)
                GPIO.output(Motor1B, GPIO.LOW)
                #sleep(5)
            if event.button == 2: #X
                print ("Extend Actuator")
                GPIO.output(Motor1A, GPIO.LOW)
                GPIO.output(Motor1B, GPIO.HIGH)
                #sleep(5)
            if event.button == 3: #Y
                print ("Extending and actuator")
                GPIO.output(Motor1A, GPIO.LOW)
                GPIO.output(Motor1B, GPIO.HIGH)

                sleep(5)

                print ("Returning actuator")
                GPIO.output(Motor1A, GPIO.HIGH)
                GPIO.output(Motor1B, GPIO.LOW)
                #sleep(5)
            if event.button == 4: #LB
                print("LB servo")
                p.ChangeDutyCycle(4.5)
                sleep(0.1)
                p.ChangeDutyCycle(0)
            if event.button == 5: #RB
                print("RB servo")
                p.ChangeDutyCycle(7)
                sleep(0.1)
                p.ChangeDutyCycle(0)

        elif event.type == pygame.JOYBUTTONUP:
            # print ("Joystick '",joysticks[event.joy].get_name(),"' button",event.button,"released.")
            if event.button >= 0 and event.button <= 3:
                arduino.stop()
        elif event.type == pygame.JOYHATMOTION:
            # print ("Joystick '",joysticks[event.joy].get_name(),"' D-Pad",event.hat," moved.")
            if event.value == (1, 0): #Right button
                print("Vex servo expand")
                q.ChangeDutyCycle(8.5)
                sleep(0.1)
                q.ChangeDutyCycle(0)
            if event.value == (-1, 0): #Left button
                #arduino.left(gear[gearIndex])
                print("vex servo contract")
                q.ChangeDutyCycle(13.5)
                sleep(0.1)
                q.ChangeDutyCycle(0)
            if event.value == (0, -1): #backward
                #arduino.backward(gear[gearIndex])
                pass
            if event.value == (0, 1): #forward
                #arduino.forward(gear[gearIndex])
                pass
            if event.value == (0, 0):
                arduino.stop()


if __name__ == '__main__':
    import sys
    app = QCoreApplication(sys.argv)
    timer.timeout.connect(haveHeardFromControllerSlot)
    if initXbox360():
        xboxTimer.timeout.connect(loopXboxRPI)
        xboxTimer.start(50)
    else:
        server = RobotServer()
        server.gotManualMessage.connect(gotManualMessageSplot)
        server.gotSensorMessage.connect(gotSensorMessageSplot)
        server.controllerDisconnected.connect(controllerDisconnectedSlot)
        server.tcpServer.newConnection.connect(controllerConnectedSlot)

    app.exec()
