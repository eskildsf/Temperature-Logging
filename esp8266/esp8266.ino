#include <Arduino.h>

#ifdef ESP8266
extern "C" {
#include "user_interface.h"
}
#endif

#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
ESP8266WiFiMulti WiFiMulti;

#include <ESP8266HTTPClient.h>
HTTPClient http;

#include <HTU21D.h>
HTU21D htu21d;

int temperature, humidity;
byte new_data = false;
unsigned long interval = 10000; // [ms]
unsigned long t;
unsigned long id;

#define ON LOW
#define OFF HIGH
#define HIGHPWM 1010

const char* website_domain = "yourdomain.tld"; // Update this line. For a test at home you can set it to '[flask_server_ip]:8080
const char* password = "1234"; // Update this line

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, OFF);

  id = system_get_chip_id();

  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP("ssid", "password"); // Update this line
  http.setReuse(true);

  // SDA - GPIO0 (D3 on the WeMos D1 Mini), SCL - GPIO3 (RX on the WeMos D1 Mini)
  while ( htu21d.begin(0, 3) != true ) {
    // Blink LED until HTU21D is functional
    analogWrite(LED_BUILTIN, HIGHPWM);
    delay(3);
    digitalWrite(LED_BUILTIN, OFF);
    delay(200);
  }
  t = -interval;
}

void loop() {
  if ( new_data = (millis() - t >= interval) ) {
    humidity = 100*htu21d.readCompensatedHumidity();
    temperature = 100*htu21d.readTemperature();
    if ( humidity != 0 && temperature != 0) {
      t = t + interval;
      analogWrite(LED_BUILTIN, HIGHPWM);
    } else {
      new_data = false;
    }
  }

  bool connection_status = (WiFiMulti.run() == WL_CONNECTED);
  if ( new_data && connection_status ) {
    http.begin((String)"http://"+website_domain+"/");
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    char payload[150];
    sprintf(payload, "deviceid=%i&temperature=%i&humidity=%i&mil=%lu&password=%s",id,temperature,humidity,t,password);
    int response = http.POST(payload);
    http.end();
    if ( response == HTTP_CODE_OK ) {
      digitalWrite(LED_BUILTIN, OFF);
      new_data = false;
    }
  }
}
