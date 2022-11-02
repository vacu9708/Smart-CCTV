#include <Adafruit_NeoPixel.h>
#include <SoftwareSerial.h>
#ifdef __AVR__
#include <avr/power.h>
#endif
#define NUMPIXELS 12
Adafruit_NeoPixel LED0(NUMPIXELS, 9, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel LED1(NUMPIXELS, 10, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel LED2(NUMPIXELS, 11, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel LED3(NUMPIXELS, 12, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel LED4(NUMPIXELS, 13, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel LEDs[5];
SoftwareSerial bluetooth(5, 4); // RXD, TXD

void adjust_LED(Adafruit_NeoPixel* LED, char R, char G, char B){
  for(int i=0; i<NUMPIXELS; i++) {
    LED->setPixelColor(i, LED->Color(R,G,B));
    LED->show();
  }
}

char is_blink[5];
void change_parking_space_LED(char parking_space, char LED_state){
  if(LED_state=='0'){ // Off
    is_blink[parking_space]=0;
    adjust_LED(&LEDs[parking_space], 0,0,0);
  }
  else if(LED_state=='1'){ // Green
    is_blink[parking_space]=0;
    adjust_LED(&LEDs[parking_space], 0,150,0);
  }
  else if(LED_state=='2'){ // Red
    is_blink[parking_space]=0;
    adjust_LED(&LEDs[parking_space], 150,0,0);
  }
  else if(LED_state=='3'){ // Parking, Orange
    is_blink[parking_space]=3;
    //adjust_LED(&LEDs[parking_space], 250,50,0);
  }
  else if(LED_state=='4') // Leaving Yellow
    is_blink[parking_space]=4;
    //adjust_LED(&LEDs[parking_space], 100,150,0);
}

void handle_signal(){
  char parking_space;
  char LED_state;
  while(bluetooth.available()){
    parking_space = bluetooth.read();
    delay(30);
    LED_state = bluetooth.read();
    if(48<=parking_space && parking_space<=57 && 48<=LED_state && LED_state<=57){
      change_parking_space_LED(atoi(&parking_space), LED_state);
      bluetooth.write('O');
      //Serial.write(parking_space); Serial.write(LED_state); Serial.write(" O\n");
      break;
    }
    else{
      //Serial.write(parking_space); Serial.write(LED_state); Serial.write(" X\n");
      bluetooth.write('X');
    }
  }
}

char blinking_orange[3];
char blinking_yellow[3];
unsigned long prev_time;
void blink_LED(){
  if(millis()-prev_time>500){
    for(char i=0; i<5; i++)
      if(is_blink[i]==3)
        adjust_LED(&LEDs[i], blinking_orange[0],blinking_orange[1],0);
      else if(is_blink[i]==4)
        adjust_LED(&LEDs[i], blinking_yellow[0],blinking_yellow[1],0);
    blinking_orange[0] = blinking_orange[0]==0? 250: 0; blinking_orange[1] = blinking_orange[1]==0? 50: 0;
    blinking_yellow[0] = blinking_yellow[0]==0? 100: 0; blinking_yellow[1] = blinking_yellow[1]==0? 150: 0;
    prev_time=millis();
  }
}

void setup() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
    LEDs[0] = LED0;
    LEDs[1] = LED1;
    LEDs[2] = LED2;
    LEDs[3] = LED3;
    LEDs[4] = LED4;
    for (char i = 0; i < 5; i++){
      LEDs[i].begin();
      adjust_LED(&LEDs[i],20,20,20);
    }
  }

  int baudrate=9600;
  bluetooth.begin(baudrate);
  Serial.begin(baudrate);

void loop() {
  handle_signal();
  blink_LED();
}
