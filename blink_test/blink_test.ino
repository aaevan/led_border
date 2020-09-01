#include <FastLED.h>

// How many leds in your strip?
#define NUM_LEDS 50

// For led chips like WS2812, which have a data line, ground, and power, you just
// need to define DATA_PIN.  For led chipsets that are SPI based (four wires - data, clock,
// ground, and power), like the LPD8806 define both DATA_PIN and CLOCK_PIN
// Clock pin only needed for SPI based chipsets when not using hardware SPI
#define DATA_PIN 7
#define CLOCK_PIN 13

// Define the array of leds
CRGB leds[NUM_LEDS];

void setup() { 
    FastLED.addLeds<WS2812, DATA_PIN, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
}

int count = 0;

void loop() {
  // Turn the LED on, then pause
  leds[count] = CRGB(255, 255, 0);
  FastLED.show();
  delay(10);
  // Now turn the LED off, then pause
  leds[count] = CRGB::Black;
  count += 1;
  count %= NUM_LEDS;
  FastLED.show();
  delay(10);
}
