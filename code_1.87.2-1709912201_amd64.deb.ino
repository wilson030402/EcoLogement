#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "DHT.h"

// Définition du type et de la broche du capteur DHT
#define DHTTYPE DHT22
#define DHTPIN 5

DHT dht(DHTPIN, DHTTYPE);

// Remplacez par vos identifiants WiFi
const char* ssid     = "Livebox-215E";
const char* password = "sZfz35nXn5h3L2rnVN";

// Adresse et port du serveur (adapté à votre réseau)
const char* serverName = "http://192.168.1.29:8888";  // Remplacez par l'IP de votre serveur

void setup() {
  Serial.begin(115200);
  delay(10);
  Serial.println("Connexion au WiFi...");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Connecté au WiFi !");
  
  dht.begin();
}

void loop() {
  // Pause de 2 secondes entre chaque mesure
  delay(2000);

  // Lecture des valeurs du capteur
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Échec de lecture du capteur DHT22 !");
    return;
  }
  
  Serial.print("Température: ");
  Serial.print(temperature);
  Serial.print(" °C, Humidité: ");
  Serial.print(humidity);
  Serial.println(" %");
  
  // Pour la date, ici on envoie une chaîne vide.
  // Si vous souhaitez envoyer le timestamp actuel, il faudra intégrer un client NTP.
  String timestamp = "";

  // Préparation des payloads JSON pour la température (ID 0) et l'humidité (ID 1)
  String tempPayload = "{\"id_capteur_actionneur\":0, \"valeur\":" + String(temperature, 2) + ", \"date_insertion\":\"" + timestamp + "\"}";
  String humidityPayload = "{\"id_capteur_actionneur\":1, \"valeur\":" + String(humidity, 2) + ", \"date_insertion\":\"" + timestamp + "\"}";
  
  if (WiFi.status() == WL_CONNECTED) {
    // Envoi de la température
    {
      WiFiClient clientTemp;
      HTTPClient httpTemp;
      String urlTemp = String(serverName) + "/add_mesure";
      httpTemp.begin(clientTemp, urlTemp);  // Utilisation de la nouvelle API
      httpTemp.addHeader("Content-Type", "application/json");
      int httpResponseCode = httpTemp.POST(tempPayload);
      if (httpResponseCode > 0) {
        Serial.print("Réponse POST température: ");
        Serial.println(httpResponseCode);
      } else {
        Serial.print("Erreur lors du POST température: ");
        Serial.println(httpTemp.errorToString(httpResponseCode).c_str());
      }
      httpTemp.end();
    }
    
    // Envoi de l'humidité
    {
      WiFiClient clientHum;
      HTTPClient httpHum;
      String urlHum = String(serverName) + "/add_mesure";
      httpHum.begin(clientHum, urlHum);  // Utilisation de la nouvelle API
      httpHum.addHeader("Content-Type", "application/json");
      int httpResponseCode = httpHum.POST(humidityPayload);
      if (httpResponseCode > 0) {
        Serial.print("Réponse POST humidité: ");
        Serial.println(httpResponseCode);
      } else {
        Serial.print("Erreur lors du POST humidité: ");
        Serial.println(httpHum.errorToString(httpResponseCode).c_str());
      }
      httpHum.end();
    }
  } else {
    Serial.println("WiFi non connecté !");
  }
}
