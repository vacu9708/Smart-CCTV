#include <SoftwareSerial.h>
//SoftwareSerial bluetooth(2,3); // RXD, TXD

void right(int speed)
{
  digitalWrite(6, LOW); 
  digitalWrite(7, HIGH); 
  analogWrite(5,speed); // 좌우 speed 
}

void left(int speed)
{
  digitalWrite(6, HIGH); 
  digitalWrite(7, LOW); 
  analogWrite(5,speed); // 좌우 speed 
}
void RL_stop()
{
  digitalWrite(6, HIGH); 
  digitalWrite(7, HIGH);   
  analogWrite(5,0); // 좌우 speed 
}
void back(int speed)
{
  digitalWrite(9, LOW); 
  digitalWrite(10, HIGH); 
  analogWrite(8,speed); // 앞뒤 speed 
}
void forward(int speed)
{
  digitalWrite(9, HIGH); 
  digitalWrite(10, LOW); 
  analogWrite(8,speed); // 앞뒤 speed 
}
void FB_stop() 
{
  digitalWrite(9, HIGH); 
  digitalWrite(10, HIGH); 
  analogWrite(8,0); 
}

char speed_parser(char car_speed){
  if(car_speed=='a')
    return 80;
  else if(car_speed=='b')
    return 90;
  else if(car_speed=='c')
    return 100;
  else if(car_speed=='d')
    return 110;
  else if(car_speed=='e')
    return 120;
  else if(car_speed=='f')
    return 130;
  else if(car_speed=='g')
    return 140;
  else if(car_speed=='h')
    return 150;
  else if(car_speed=='i')
    return 160;
  else if(car_speed=='j')
    return 170;
  else if(car_speed=='k')
    return 180;
  else if(car_speed=='l')
    return 190;
  else if(car_speed=='m')
    return 200;
  else if(car_speed=='n')
    return 210;
  else if(car_speed=='o')
    return 220;
  else if(car_speed=='p')
    return 230;
  else if(car_speed=='q')
    return 240;
  else if(car_speed=='z')
    return 255;
}

short delay_parser(char accel_time){
  if(accel_time=='a')
    return 100;
  else if(accel_time=='b')
    return 200;
  else if(accel_time=='c')
    return 300;
  else if(accel_time=='d')
    return 400;
  else if(accel_time=='e')
    return 500;
  else if(accel_time=='f')
    return 600;
  else if(accel_time=='g')
    return 700;
  else if(accel_time=='h')
    return 800;
  else if(accel_time=='i')
    return 900;
  else if(accel_time=='j')
    return 1000;
}

void drive(char control, char car_speed, char _accel_time){
  car_speed=speed_parser(car_speed);
  short accel_time=delay_parser(_accel_time);
  if(control=='w'){
    forward(car_speed);
    delay(accel_time);
    FB_stop();
  }
  else if(control=='s'){
    back(car_speed);
    delay(accel_time);
    FB_stop();
  }
  else if(control=='p')
    FB_stop();
  else if(control=='l')
    left(car_speed);
  else if(control=='r')
    right(car_speed);
  else if(control=='P')
    RL_stop();
}

void handle_signal(){
  char control=' ', car_speed=' ', accel_time=' ';
  while(Serial1.available()){
    control = Serial1.read();
    if(control=='Q'){
      digitalWrite(2, HIGH);
      Serial1.write('O');
      return;
    }
    else if(control=='W'){
      digitalWrite(2, LOW);
      Serial1.write('O');
      return;
    }
    delay(25);
    car_speed=Serial1.read();
    delay(25);
    accel_time=Serial1.read();
    if(65<=control && control<=122 && 65<=car_speed && car_speed<=122 && 65<=accel_time && accel_time<=122){
      drive(control, car_speed, accel_time);
      Serial1.write('O');
      //Serial.write(control); Serial.write(car_speed); Serial.write(accel_time); Serial.write(" O\n");
      break;
    }
    else{
      //Serial.write(control); Serial.write(car_speed); Serial.write(accel_time); Serial.write(" X\n");
      Serial1.write('X');
    }
  }
}

void setup() {
  int baudrate=9600;
  Serial.begin(baudrate);
  Serial1.begin(baudrate);

  // 블루투스
  pinMode(2,OUTPUT);
  digitalWrite(2, LOW);
  
  pinMode(6,OUTPUT);
  pinMode(7,OUTPUT);
  pinMode(9,OUTPUT);
  pinMode(10,OUTPUT);
}

void loop() {
  handle_signal();
}
