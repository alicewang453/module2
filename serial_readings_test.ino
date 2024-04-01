const int buttonPin = 17; // GPIO pin used for the button
const int potPin = 13; // Analog pin used for the potentiometer

void setup() {
  Serial.begin(115200);
  pinMode(buttonPin, INPUT_PULLUP); // Enable internal pull-up resistor
}

void loop() {
  int potValue = analogRead(potPin); // Read the potentiometer value
  int buttonState = digitalRead(buttonPin); // Read the button state
  
  // Print the values to the Serial Monitor
  Serial.print("Potentiometer Value: ");
  Serial.println(potValue);
  Serial.print("\tButton State: ");
  Serial.println(buttonState);

  delay(1000); // Small delay to make the serial output more readable
}
