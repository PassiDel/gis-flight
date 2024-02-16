#include <Adafruit_NeoPixel.h>
#include "HardwareSerial.h"

#define PIXELS 5632
#define MAX_BUFFERED_COMMANDS 200 // Adjust this as needed
#define RX_BUFFER_SIZE 1024
#define STRIP_PIN 26
#define RX_PIN 12
#define TX_PIN 14

Adafruit_NeoPixel strip;
String commandBuffer[MAX_BUFFERED_COMMANDS];
int bufferCount = 0;
unsigned long lastUpdateMillis = 0;
int wait_until_buffer_eval = 0; // ms 

void setup() {
  Serial.begin(460800, SERIAL_8N1, RX_PIN, TX_PIN);
  Serial.setRxBufferSize(RX_BUFFER_SIZE);

  strip = Adafruit_NeoPixel(PIXELS, STRIP_PIN, NEO_GRB + NEO_KHZ800);
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
  if (bufferCount > 0 && millis() > lastUpdateMillis + wait_until_buffer_eval) {
    for (int i = 0; i < bufferCount; i++) {
      parseAndSetPixel(commandBuffer[i]);
    }
    strip.show();
    
    // print details to serial
    Serial.print("U ");
    Serial.print(millis() - lastUpdateMillis);
    Serial.print(" B ");
    Serial.println(bufferCount);
    bufferCount = 0; // Reset buffer count after updating
    lastUpdateMillis = millis(); // Reset the update timer
  }
}

void parseAndSetPixel(String data) {
  if (data.startsWith("W ")) {
    // Handle wait command
    data.remove(0, 2); // Remove "W " from the string
    wait_until_buffer_eval = data.toInt(); // Convert the remaining string to int
  } else if (data == "C") {
    // Handle clear command
    strip.clear();
  } else {
    // Parse the pixel setting command
    int pixel_index, r, g, b;
    if (sscanf(data.c_str(), "%d,%d,%d,%d", &pixel_index, &r, &g, &b) == 4) {
      strip.setPixelColor(pixel_index, strip.Color(r, g, b));
    }
  }
}
