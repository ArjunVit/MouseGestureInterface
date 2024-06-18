#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;
Adafruit_MPU6050 mpu;
const int buttonPin1 = 32;
const int buttonPin2 = 34;
int buttonState1 = 0;
int buttonState2 = 0;
int caliNum;
float calix = 0;
float caliy = 0;
float caliz = 0;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin1, INPUT);
  pinMode(buttonPin2, INPUT);
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }   
  Serial.println("MPU6050 Found!");
  SerialBT.begin("ESP32Test");
  Serial.println("Pair device to ESP32Test");
  while(!SerialBT.available()) {
    Serial.print(".");
    delay(500);
  }
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  String btline="";
  btline = btline + a.acceleration.x;
  btline = btline + " ";
  delay(10);
  btline = btline + a.acceleration.y;
  btline = btline + " ";
  delay(10);
  btline = btline + a.acceleration.z;
  btline = btline + " ";
  delay(10);
  btline = btline + (g.gyro.x-calix);
  btline = btline + " ";
  delay(10);
  btline = btline + (g.gyro.y-caliy);
  btline = btline + " ";
  delay(10);
  btline = btline + (g.gyro.z-caliz);
  btline = btline + " ";
  delay(10);
  buttonState1 = digitalRead(buttonPin1);
  buttonState2 = digitalRead(buttonPin2);
  if (buttonState1 == HIGH) {
    btline = btline + "1 ";
  } else {
    btline = btline + "0 ";
  }
  if (buttonState2 == HIGH) {
    btline = btline + "1 ";
  } else {
    btline = btline + "0 ";
  }
  buttonState1 = LOW;
  buttonState2 = LOW;
  Serial.println(btline);
  SerialBT.println(btline);
}
