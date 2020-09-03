#include <FastLED.h>

#define NUM_LEDS 50
#define DATA_PIN 7

CRGB leds[NUM_LEDS];

void setup() {
  // initialize serial:
  // make the pins outputs:
  FastLED.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  leds[0] = CRGB(0, 255, 0);
  leds[1] = CRGB(255, 0, 0);
  leds[2] = CRGB(0, 0, 255);
  FastLED.show();
  Serial.begin(57600);
}

int count = 0;

void loop() {
  //FastLED.show();
  // if there's any serial available, read it:
  while (Serial.available() > 0) {

    // look for the next valid integer in the incoming serial stream:
    //int led_index = Serial.parseInt();
    int index = Serial.parseInt();
    int red = Serial.parseInt();
    // do it again:
    int green = Serial.parseInt();
    // do it again:
    int blue = Serial.parseInt();

    // look for the newline. That's the end of your sentence:
    if (Serial.read() == '\n') {
      //print the three numbers in one string as hexadecimal:
      Serial.print(index);
      Serial.print(',');
      Serial.print(red);
      Serial.print(',');
      Serial.print(green);
      Serial.print(',');
      Serial.println(blue);
      Serial.println(count);
      //leds[count] = CRGB(red, green, blue);
      leds[index] = CRGB(red, green, blue);
      count = (count + 1) % NUM_LEDS;
      FastLED.show();
    }
  }
}
