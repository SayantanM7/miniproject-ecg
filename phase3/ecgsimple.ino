const int ecgPin = 1;  // Analog pin connected to AD8232 OUTPUT

void setup() {
  Serial.begin(115200);  // Start serial at high baud rate for smooth plot
}

void loop() {
  int ecgValue = analogRead(ecgPin);  // Read ECG analog signal
  Serial.println(ecgValue);           // Print to Serial Plotter
  delay(3);                           // 3 ms delay
}
