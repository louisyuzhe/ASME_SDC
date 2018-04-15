"""commands:
1: drive motors
"""
from serial import Serial
print("new")
class Arduino():
    """
    An interface with Arduino, which is attached to the RPi by the serial pins.
    """
    def __init__(self, serialPort):
        self.serialPort = Serial(serialPort, baudrate=9600, timeout=3.0)
        
    def write(self, message):
        message.append((256-sum(message))%256)
        return self.serialPort.write(message)

    def writeDirectly(self, message):
        return self.serialPort.write(message)

    def read(self, numBytes):
        return None

    def motor(self, device, value1, value2):
        if value1 < 0: value1+=256
        if value2 < 0: value2+=256
        return self.write([1, device, value1, value2])

    #def drive(self, drive, turn):
     #   return self.motor(6, drive, turn)

    def drive(self, drive, turn):
        return self.motor(4, drive, 0)

    def turn(self, drive, turn):
        return self.motor(5, 0, turn)

    def tankDrive(self, leftSpeed, rightSpeed):
        return self.motor(7, leftSpeed, rightSpeed)

    def stop(self):
        return self.drive(0, 0)

    def left(self, speed):
        return self.drive(speed, -100)

    def right(self, speed):
        return self.drive(speed, 100)

    def forward(self, speed):
        return self.drive(speed, 0)

    def backward(self, speed):
        return self.drive(-speed, 0)
