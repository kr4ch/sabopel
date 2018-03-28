#include "Arduino.h"

#define SENSOR_A 2
#define SENSOR_B 3
#define SENSOR_C 4
#define LED_READY 13
#define CMD_READY 0x56 // command for restarting
#define CMD_RESTART 0x59 // command for restarting

union Data{
    char myByte[4];
    long myLong;
};

void setup() {
  Serial.end();                  // Close any previously established connections
  Serial.begin(115200);            // Serial output back to computer.  On.


  pinMode(SENSOR_A, INPUT);
  pinMode(SENSOR_B, INPUT);
  pinMode(SENSOR_C, INPUT);

  pinMode(LED_READY, OUTPUT);
  digitalWrite(LED_READY, LOW);
}

void loop() {
  unsigned long StartTime, StopTime, MiddleTime, RunTime, HalfTime;
  union Data myUnion; 
  char incomingByte;
  
/*  // wait until reset button is pressed
  while(!digitalRead(RESET))
  {
    delay(500);
  }

  // wait until reset button is released
  while(digitalRead(RESET))
  {
    delay(500); 
  }*/


  // wait for the command from the python scipt to get ready
  incomingByte = 0;
  
  while(incomingByte != CMD_READY)
  {
    if (Serial.available() > 0)
    {
      incomingByte = Serial.read();
      Serial.print(incomingByte);
    }
  }

  Serial.print("R");

  digitalWrite(LED_READY, HIGH); // ready signal
  
  // wait for Sensor A
  while(!digitalRead(SENSOR_A))
  {
  /*  if (Serial.available() > 0)
    {
      incomingByte = Serial.read();
      Serial.print(incomingByte);
    }*/
  }
 // if(incomingByte != CMD_RESTART)
//  {
    StartTime = micros();
    Serial.print("A");

    digitalWrite(LED_READY, LOW); // clear ready signal
//  }

  
  // wait for Sensor B
  while(!digitalRead(SENSOR_B))
  {
   /* if (Serial.available() > 0)
    {
      incomingByte = Serial.read();
      Serial.print(incomingByte);
    }*/
  }
//  if(incomingByte != CMD_RESTART)
//  {
    MiddleTime = micros();
    Serial.print("B");
    HalfTime = MiddleTime-StartTime;
    myUnion.myLong = HalfTime;
    Serial.print(myUnion.myByte[0]); // MSB from long (HalfTime)
    Serial.print(myUnion.myByte[1]);
    Serial.print(myUnion.myByte[2]);
    Serial.print(myUnion.myByte[3]);
//  }
  
 
  // wait for Sensor C
  while(!digitalRead(SENSOR_C))
  {
   /* if (Serial.available() > 0)
    {
      incomingByte = Serial.read();
      Serial.print(incomingByte);
    }*/
  }
//  if(incomingByte != CMD_RESTART)
//  {
    StopTime = micros();
    Serial.print("C");
    RunTime = StopTime-StartTime;
    myUnion.myLong = RunTime;
    Serial.print(myUnion.myByte[0]); // MSB from long (RunTime)
    Serial.print(myUnion.myByte[1]);
    Serial.print(myUnion.myByte[2]);
    Serial.print
    (myUnion.myByte[3]);
//  }
}
