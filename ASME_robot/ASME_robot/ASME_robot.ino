#include "SDCMotorControl.h"
#include <PID_v1.h>

KangarooSDC motorK(Serial3);
void setup() {
	motorK.begin();
	Serial1.begin(9600);
	Serial.begin(9600);
	Serial.println("Motor control started!");
}

void loop() {
	motorK.loop();
	serialEvent();
}

void serialEvent() {
	while (Serial1.available() > 4) {
		char message[5];
		Serial1.readBytes(message, 5);
		if (checkSum(message, 5))
		{
			char command = message[0];
			char device = message[1];
			char value1 = message[2];
			char value2 = message[3];
			switch (command)
			{
			case 1:
				switch (device)
				{
				case 0:
					//Emergency Stop. Should stop all motors
					motorK.motors->drive(0, 0);
					break;
				case 1:
					break;
				case 2:
					break;
				case 3:
					break;
				case 4:
					break;
				case 5:
					break;
				case 6:
					motorK.motors->drive((signed char)value1, (signed char)value2);
					break;
				case 7:
					motorK.motors->tankDrive((signed char)value1, (signed char)value2);
					break;
				default:
					Serial.println("unhanddle command: " + String(command) + " " + String(device) + " " + String(value1) + " " + String(value2));
					break;
				}
			}
		}
	}
}
bool checkSum(char arrayNum[], int len) {
	char sum = 0;
	for (int i = 0; i < len; i++)
	{
		sum += arrayNum[i];
	}
	if (sum == 0)
	{
		return true;
	}
	else
	{
		Serial.print("Checksum fails.");
		for (int i = 0; i < len; i++)
		{
			Serial.print(arrayNum[i]);
			Serial.print(" ");
		}
		Serial.println();
		return false;
	}
}