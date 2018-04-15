import RPi.GPIO as GPIO
import math
import xbox
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 50)

p.start(7.5)

Motor1A = 16
Motor1B = 18
Motor2A = 21 #connected
Motor2B = 23 #connected

 
GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)



 
# def updateServo(pwm, angle):
#     duty = float(angle) / 10.0 + 2.5
#     pwm.ChangeDutyCycle(duty)
 
def angleFromCoords(x,y):
    motion = 0.0;
    if x==0.0 and y==0.0:
	motion = 0;
     #   angle = 90.0
    elif -1.0<x<=1.0 and y==1.0:
	motion = 1; #front
        #angle = math.degrees(math.atan(y/x))  if x!=0.0 else 90.0
    elif -1.0<=x<1.0 and y==-1.0:
	motion = 2; #reverse
        #angle = math.degrees(math.atan(y/x))
        #angle += 180.0
    elif x==-1.0 and -1.0<y<=1.0:
	motion = 3; #left
        #angle = math.degrees(math.atan(y/x))
        #angle += 180.0
    elif x==1.0 and -1.0<=y<1.0:
	motion = 4; #right
        #angle = math.degrees(math.atan(y/x)) if x!=0.0 else -90.0
        #angle += 360.0
    return motion
def forward(GPIO,Motor1A,Motor1B,Motor2A,Motor2B):
    GPIO.output(Motor1A,GPIO.HIGH)
    GPIO.output(Motor1B,GPIO.LOW)
    GPIO.output(Motor2A,GPIO.HIGH)
    GPIO.output(Motor2B,GPIO.LOW)

def backwards(GPIO,Motor1A,Motor1B,Motor2A,Motor2B):
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.HIGH)
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.HIGH)
    
def right(GPIO,Motor1A,Motor1B,Motor2A,Motor2B):
    GPIO.output(Motor1A,GPIO.HIGH)
    GPIO.output(Motor1B,GPIO.LOW)
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.HIGH)
    
def left(GPIO,Motor1A,Motor1B,Motor2A,Motor2B):
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.HIGH)
    GPIO.output(Motor2A,GPIO.HIGH)
    GPIO.output(Motor2B,GPIO.LOW)

def stop(GPIO,Motor1A,Motor1B,Motor2A,Motor2B):
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.LOW)
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.LOW)

if __name__ == '__main__':
    joy = xbox.Joystick()

   
    while not joy.Back():
        
        x, y = joy.rightStick()
        motion = angleFromCoords(x,y)
        
        if joy.Y() == 1:
            print("Y servo")
            p.ChangeDutyCycle(2.5)
            sleep(1)
            #p.ChangeDutyCycle(2.5)  # turn towards 0 degree
	    #sleep(1)
        if joy.A() == 1:
            print("A servo")
            p.ChangeDutyCycle(12.5)
            sleep(1)
	
       	if motion == 1:
            print("forward")
	    forward(GPIO,Motor1A,Motor1B,Motor2A,Motor2B)
        elif motion == 2:
	    print("reverse")
            backwards(GPIO,Motor1A,Motor1B,Motor2A,Motor2B)
       	elif motion == 3:
	    print("left")
	    left(GPIO,Motor1A,Motor1B,Motor2A,Motor2B)
	elif motion == 4:
            print("right")
            right(GPIO,Motor1A,Motor1B,Motor2A,Motor2B)
        else:
            stop(GPIO,Motor1A,Motor1B,Motor2A,Motor2B)
            

    GPIO.cleanup()
    joy.close()




