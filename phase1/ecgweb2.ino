#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "mySSID";
const char* password = "myPassword";

WebServer server(80);

void setup() {
  Serial.begin(115200);
  
  // Start WiFi AP
  WiFi.softAP(ssid, password);
  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());

  // ECG endpoint with CORS headers (NEW)
  server.on("/ecg", []() {
    // Add CORS headers (NEW)
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.sendHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
    server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
    
    int ecgValue = analogRead(3);  // Read from GPIO1 (A0)
    server.send(200, "text/plain", String(ecgValue));
  });

  // Handle preflight OPTIONS requests (NEW)
  server.on("/ecg", HTTP_OPTIONS, []() {
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.sendHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
    server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
    server.send(204);
  });
  
  server.begin();
}

void loop() {
  server.handleClient();
  delay(100);  // ~100Hz sampling
}
