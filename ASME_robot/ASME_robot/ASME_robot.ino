#include <Kangaroo.h>
#include <PID_v1.h>
#include "SimpleTimer.h"
#include <Wire.h>
#include "SDCMotorControl.h"
#define MESSAGE_LENGTH 8
#define I2CAddress 7
/*Not all pins on the Mega and Mega 2560 support change interrupts, so only the following can be used for RX: 10, 11, 12, 13, 14, 15, 50, 51, 52, 53, A8 (62), A9 (63), A10 (64), A11 (65), A12 (66), A13 (67), A14 (68), A15 (69).
*/
long lastTime = 0;
SimpleTimer timer;
KangarooSDC motorK(10, 11);
//At a higher resoultion, speed limit is lower

void setup() {
	Serial.begin(9600);
		i2cSetup();
	Serial.println("start begin setup");
	motorK.begin();
	Serial.println("end setup");

}
void loop() {
	timer.run();
	motorK.loop();
	
	//{@Plot.Velocity.Velo.Red aX}, {@Plot.Position.Min.Green linearK.min1}, setValue is {setValue =?},  {@Plot.Speed.SetSpeed.Red setMotorSpeed}, {@Plot.Speed.CurrentSpeed.Green motorK.status1->value()}, setMotorSpeed is {setMotorSpeed =?}
	delay(1);
}


void i2cSetup() {
	Wire.begin(I2CAddress);
	Wire.setClock(96000L);
	Wire.onReceive(onI2CReceive);
	Wire.onRequest(onI2CRequest);

}

void onI2CReceive(int numByte) {
	int message[MESSAGE_LENGTH];
	int i = 0;
	for (int i = 0; i < numByte; i++) {
		message[i] = Wire.read();
	}
	int systemCommand = message[0];
	// 1 - from a controller
	// 2 - from the pi directly
	// 3 - x
	int command = message[1];
	int device = message[2];
	int value = message[3];
	switch (systemCommand)
	{
	case 0:
		break;
	case 1: //pass through
		switch (command)
		{
		case 1:
			switch (device)
			{
			case 1:
				motorK.motors->setDrive((signed char)value);
				motorK.motors->mode = 0;
				break;
			case 2:
				motorK.motors->setTurn((signed char)value);
				break;
			case 3:
				break;
			case 4:
				break;
			case 5:
				break;
			case 6: //channel 1 and 2 together
				break;
			case 8:
				motorK.motors->setPos(2);
				break;
			default:
				break;
			}
			//Serial.println(value);
		}
	default:
		break;
	}
}

void onI2CRequest() {
	int linearActPos = motorK.linearActuatorPair->getPos();
	int leftMotorSpeed = (motorK.motors->getLeftMotorS());
	int rightMotorSpeed = (motorK.motors->getRightMotorS());

	//Wire.write(LINEAR_ACTUATOR_1); // Device ID
	//Wire.write(linearActPos); //Linear actuator current position
	Wire.write(leftMotorSpeed); //Speed for left motor speed
	Wire.write(rightMotorSpeed); // Speed for right motor speed
}

