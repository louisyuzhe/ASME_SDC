#include "SDCMotorControl.h"
/*!
Constructor
*/
LinearActuator::LinearActuator(KangarooSerial& K, char name):KangarooChannel(K, name)
{
}
/*!
Initiates the Kangaroo. Gets min and max positions for Linear Actuator.
*/
void LinearActuator::begin() {
	start();
	getExtremes(); //Getting max and min value for position
}
/*!
Extends Linear Actuator to target position with set speed while in range.
Powers down when completed.
*/
void LinearActuator::loop()
{
	if (targetVal >= min && targetVal <= max && (targetVal != lastVal || speed != lastSpeed )) {
		done = false;
		p(targetVal, speed);
		lastVal = targetVal;
		lastSpeed = speed;
	}

	status = getP();
	if (status.done()) {
		powerDown();
		done = true;
	}
}
/*!
Computes min and max values for position of Linear Actuator. 
Sets default max Speed.
*/
void LinearActuator::getExtremes()
{
		long absMin = getMin().value();
		long absMax = getMax().value();
		long safeBound = (absMax - absMin)*0.02;
		min = (absMin + safeBound);
		max = absMax - safeBound;
		maxSpeed =208;
		//maxSpeed = 0.5 * (absMax - absMin);
		Serial.println("max speed is: " + String(maxSpeed));
}
/*!
Sets target position for Linear Actuator between 0 and 100.
*/
void LinearActuator::setTargetPosDirect(long pos)
{
	if (targetVal >= min && targetVal <= max) {
		targetVal = pos;
	}
}
/*!
Sets target position and speed for Linear Actuator.
*/
void LinearActuator::setTargetVal(long pos, long newSpeed) { //val = 0% to 100%
	setTargetPos(pos);
	setSpeed(newSpeed);
}
/*!
Sets target position for Linear Actuator scaled between min and max.
*/
void LinearActuator::setTargetPos(long pos) { 
	if (pos >= 0 && pos <= 100) {
		targetVal = map(pos, 0, 100, min, max);
	}
}

/*!
Sets speed for Linear Actuator scaled between 0 and max speed.
*/
void LinearActuator::setSpeed(long newSpeed) { 
	if (newSpeed >= 0 && newSpeed <= 100) {
		speed = map(newSpeed, 0, 100, 0, maxSpeed);
	}
}
/*!
Gets current position of Linear Actuator.
*/
long LinearActuator::getCurrentVal()
{
	return status.value();
}

Motor::Motor(KangarooSerial& K, char name) :KangarooChannel(K, name)
{
}
void Motor::begin()
{
	start();
}
void Motor::setTargetPos(long pos)
{
	mode = 1;
	targetPos = pos;
}
void Motor::loop()
{
	long tempSpeed = speed;
	//Serial.println("tempSpeed "+String(tempSpeed));
	//Serial.println("lastSpeed " + String(lastSpeed));
	//Serial.println("speedLimit " + String(speedLimit));
	if (tempSpeed != lastSpeed && tempSpeed >= -speedLimit && tempSpeed <= speedLimit)
	{
		s(tempSpeed);
		lastSpeed = tempSpeed;

	}
	status = getS();
}
void Motor::setTargetSpeed(long speed) {
	if (speed >= -100 && speed <= 100) {
		this->speed = map(speed, -100, 100, -speedLimit, speedLimit);
	}
}
long Motor::getCurrentSpeed()
{
	return status.value();
}
void Motor::setSpeedLimit(long speed)
{
	if (speed > 0) {
		speedLimit = speed;
	}
}
void Motor::move(long angle, long speed)
{
	long val = angle / 360 * 2040;
	pi(val, speed).wait();
	//done = true;
}

Motors::Motors(KangarooSerial & K, char name)
{
	channel[0] = new Motor(K, name);
	channel[1] = new Motor(K, name + 1);
	channel[2] = new Motor(K, name + 2);
	channel[3] = new Motor(K, name + 3);
	for (int i = 0;i < 4;i++) {
		channel[i]->setSpeedLimit(3000);
	}

}
void Motors::loop()
{
	for (int i = 0; i < 4; i++) {
		channel[i]->mode = mode;
	}
	if (mode == 1 && alreadySetTargetPos == false) {
		if (angle <= 180 && angle >= -180) {
			long leftPos;
			long rightPos;
			if (angle < 0)
			{
				leftPos = -angle;
				rightPos = angle;
			}
			else if (angle > 0)
			{
				leftPos = angle;
				rightPos = -angle;
			}
			else {
				leftPos = targetPos;
				rightPos = targetPos;
			}
			channel[FRONT_LEFT]->setTargetPos(-leftPos);
			channel[FRONT_RIGHT]->setTargetPos(-rightPos);
			alreadySetTargetPos = true; //fix this
		}
	}
	long tempTurn = turn;
	long tempDrive = drive;
	if ((tempDrive <= 100 && tempDrive >= -100) && (tempTurn <= 100 && tempTurn >= -100)) {
		long leftSpeed = tempDrive;
		long rightSpeed = tempDrive;
		if (tempTurn == -100) {
			leftSpeed = -tempDrive;
		}
		else if (tempTurn < 0 && tempTurn >-100) {
			leftSpeed = tempDrive * (1 + (float)tempTurn / 100);
		}
		else if (tempTurn == 0) {
		}
		else if (tempTurn < 100 && tempTurn > 0) {
			rightSpeed = tempDrive * (1 - (float)tempTurn / 100);
		}
		else if (tempTurn == 100) {
			rightSpeed = -tempDrive;
		}
		channel[FRONT_LEFT]->setTargetSpeed(-leftSpeed);
		channel[FRONT_RIGHT]->setTargetSpeed(-rightSpeed);
		channel[REAR_LEFT]->setTargetSpeed(leftSpeed);
		channel[REAR_RIGHT]->setTargetSpeed(rightSpeed);
	}
	for (int i = 0; i < 4; i++)
	{
		if (channel[i]->done == true)
		{
			channel[i]->done == false;
			channel[i]->setTargetSpeed(0);
		}
		channel[i]->loop();
	}
}
void Motors::begin()
{
	for (int i = 0; i < 4; i++) {
		channel[i]->begin();
	}
}
long Motors::getLeftMotorS()
{
	return map(-channel[FRONT_LEFT]->getCurrentSpeed(), -(channel[FRONT_LEFT]->speedLimit), channel[FRONT_LEFT]->speedLimit, -100, 100);
}

long Motors::getRightMotorS()
{
	return map(channel[FRONT_RIGHT]->status.value(), -(channel[FRONT_RIGHT]->speedLimit), channel[FRONT_RIGHT]->speedLimit, -100, 100);
}

void Motors::setDrive(long drive)
{
	if (drive >= -100 && drive <= 100) {
		this->drive = drive;
	}
}
void Motors::setTurn(long turn)
{
	if (turn >= -100 && turn <= 100) {
		this->turn = turn;
	}
}
void Motors::clearAngle()
{
	angle = 0;
}
void Motors::setPos(long pos)
{
	mode = 1;
	targetPos = pos*2040;
	alreadySetTargetPos == false;
}
void Motors::setAngle(long angle)
{
	if (angle >= -180 && angle <= 180)
	{
		mode = 1;
		this->angle = angle*2040;
		alreadySetTargetPos == false;
	}
}
/*!
Constructor. Initilizes Arduino pins connected to the Kangaroo.
\param potPin the Arduino analog pin number. Default is 0.
*/
KangarooSDC::KangarooSDC(int rxPin, int txPin)
{
	SerialPort = new SoftwareSerial(rxPin, txPin);
	K = new KangarooSerial(*SerialPort);
	motors = new Motors(*K, '3');
	//linearActuatorPair = new LinearActuatorPair(*K, '1');
}
/*!
Executes the loop of the right Linear Actuator
*/
void KangarooSDC::loop()
{
	motors->loop();
	//linearActuatorPair->loop();
}
/*!
Initiates Serial Communication.
Executes begin methods of all Linear Actuators and Motors.
*/
void KangarooSDC::begin() {
	SerialPort->begin(9600);
	SerialPort->listen();
	motors->begin();
	//linearActuatorPair->begin();
}