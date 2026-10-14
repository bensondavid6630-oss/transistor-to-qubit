// Level 1: observe Vin = 0 -> LED OFF, Vin = 1 -> LED ON on a real transistor switch.
// Wiring (Arduino Uno, 5 V):
//   D5 -> 10k -> base of 2N2222 / BC547   (emitter to GND)
//   5V -> LED -> 330 ohm -> collector
//   Collector -> A0 (read Vout)
// ESP32 (3.3 V): use a 2:1 divider on the collector before the ADC pin.

const int BASE  = 5;
const int SENSE = A0;

void setup() {
  pinMode(BASE, OUTPUT);
  Serial.begin(115200);
  Serial.println("Vin,Vcollector,LED");
}

void loop() {
  for (int bit = 0; bit <= 1; bit++) {
    digitalWrite(BASE, bit);                       // classical bit -> transistor
    delay(400);
    float vout = analogRead(SENSE) * 5.0 / 1023.0;  // output is inverted (NOT gate)
    Serial.print(bit);  Serial.print(",");
    Serial.print(vout); Serial.print(",");
    Serial.println(bit ? "ON" : "OFF");
    delay(600);
  }
}
