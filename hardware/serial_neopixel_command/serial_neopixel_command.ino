#include <Adafruit_NeoPixel.h>
#include "HardwareSerial.h"

#define PIXELS 5632
#define MAX_BUFFERED_COMMANDS 500 // Adjust this as needed
#define STRIP_PIN 26
#define RX_PIN 12
#define TX_PIN 14

Adafruit_NeoPixel strip;
String commandBuffer[MAX_BUFFERED_COMMANDS];
int bufferCount = 0;
unsigned long lastUpdateMillis = 0;

void setup() {
  Serial.begin(460800, SERIAL_8N1, RX_PIN, TX_PIN);
  //Serial2.begin(115200);

  strip = Adafruit_NeoPixel(PIXELS, STRIP_PIN, NEO_GRB + NEO_KHZ800);
  //strip.setBrightness(10);
  strip.begin();
  delay(4);

  strip.clear();
  strip.show();
  
  Serial.println("setup");
}

void loop() {
  while (Serial.available()) {
    // Store incoming command in the buffer
    String data = Serial.readStringUntil('\\n');
    if (bufferCount < MAX_BUFFERED_COMMANDS) {
      commandBuffer[bufferCount++] = data;
    }
  }

  // Update pixels at the specified interval
  if (bufferCount > 0) {
    Serial.print("U ");
    Serial.print(millis() - lastUpdateMillis);
    Serial.print(" B ");
    Serial.println(bufferCount);

    for (int i = 0; i < bufferCount; i++) {
      parseAndSetPixel(commandBuffer[i]);
    }
    lastUpdateMillis = millis(); // Reset the update timer
    
    strip.show();
    
    bufferCount = 0; // Reset buffer count after updating
  }
}

void parseAndSetPixel(String data) {
  int pixel_index, r, g, b;

  // Parse the data
  sscanf(data.c_str(), "%d,%d,%d,%d", &pixel_index, &r, &g, &b);

  strip.setPixelColor(pixel_index, strip.Color(r, g, b));

}
