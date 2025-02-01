#include <ESP8266WiFi.h>
#include "DHT.h"

// Définir le type de capteur DHT utilisé
#define DHTTYPE DHT22

// Définir la broche où le DHT22 est connecté (GPIO5 correspond à D1 sur certaines cartes)
#define DHTPIN 5

// Initialiser le capteur DHT
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // Initialiser la communication série pour le débogage
  Serial.begin(115200);
  Serial.println("Démarrage du lecteur DHT22 sur ESP8266");

  // Initialiser le capteur DHT
  dht.begin();
}

void loop() {
  // Attendre quelques secondes entre les lectures
  delay(2000);

  // Lire l'humidité relative
  float humidity = dht.readHumidity();
  
  // Lire la température en Celsius
  float temperature = dht.readTemperature();

  // Vérifier si les lectures ont échoué
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Échec de lecture du capteur DHT22 !");
    return;
  }

  // Afficher les valeurs lues sur le moniteur série
  Serial.print("Humidité: ");
  Serial.print(humidity);
  Serial.print(" %\t");
  Serial.print("Température: ");
  Serial.print(temperature);
  Serial.println(" °C");
}
