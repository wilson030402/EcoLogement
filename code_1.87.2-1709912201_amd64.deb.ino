#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include "DHT.h"

// ==== Informations WiFi et serveur ====

// Remplacez par vos identifiants WiFi
const char* ssid     = "Livebox-215E";
const char* password = "sZfz35nXn5h3L2rnVN";

// Adresse IP et port du serveur où tourne votre code Python
const char* serverIP   = "192.168.1.29";
const int   serverPort = 8888;
String serverName = String("http://") + serverIP + ":" + String(serverPort);

// URL pour récupérer les mesures via GET (endpoint /get_mesures)
String getMesuresURL = serverName + "/get_mesures";

// ==== Configuration du capteur DHT ====

// Définition du type et de la broche du capteur DHT
#define DHTTYPE DHT22
#define DHTPIN 5
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(100);
  
  // Configuration de la LED intégrée (généralement l'ESP8266 utilise une LED inversée)
  pinMode(LED_BUILTIN, OUTPUT);

  // Connexion au WiFi
  Serial.println("Connexion au WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connecté !");
  Serial.print("Adresse IP : ");
  Serial.println(WiFi.localIP());
  
  // Initialisation du capteur DHT
  dht.begin();
}

void loop() {
  // -------------------------------
  // PARTIE 1 : Lecture du capteur DHT22 et envoi des mesures
  // -------------------------------
  delay(2000);  // Pause de 2 secondes entre chaque mesure

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Échec de lecture du capteur DHT22 !");
  } else {
    Serial.print("Température: ");
    Serial.print(temperature);
    Serial.print(" °C, Humidité: ");
    Serial.print(humidity);
    Serial.println(" %");
    
    // Pour la date, ici on envoie une chaîne vide.
    // Vous pouvez intégrer un client NTP pour envoyer le timestamp actuel.
    String timestamp = "";

    // Préparation du payload JSON pour la température (ID 0) et l'humidité (ID 1)
    String tempPayload = "{\"id_capteur_actionneur\":0, \"valeur\":" + String(temperature, 2) + 
                         ", \"date_insertion\":\"" + timestamp + "\"}";
    String humidityPayload = "{\"id_capteur_actionneur\":1, \"valeur\":" + String(humidity, 2) + 
                             ", \"date_insertion\":\"" + timestamp + "\"}";
    
    // --- Envoi de la température ---
    {
      WiFiClient clientTemp;
      HTTPClient httpTemp;
      String urlTemp = serverName + "/add_mesure";
      httpTemp.begin(clientTemp, urlTemp);
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
    
    // --- Envoi de l'humidité ---
    {
      WiFiClient clientHum;
      HTTPClient httpHum;
      String urlHum = serverName + "/add_mesure";
      httpHum.begin(clientHum, urlHum);
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
  }
  
  // -------------------------------
  // PARTIE 2 : Récupération des mesures depuis le serveur
  // -------------------------------
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, getMesuresURL);
    
    int httpCode = http.GET();
    if (httpCode > 0) {
      Serial.print("Code HTTP GET : ");
      Serial.println(httpCode);
      
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        Serial.println("Réponse GET /get_mesures:");
        Serial.println(payload);
        
        // Pour parser le JSON, ajustez la capacité selon la taille attendue.
        const size_t capacity = JSON_ARRAY_SIZE(20) + 20 * JSON_OBJECT_SIZE(4);
        DynamicJsonDocument doc(capacity);
        
        DeserializationError error = deserializeJson(doc, payload);
        if (error) {
          Serial.print("Erreur de désérialisation JSON: ");
          Serial.println(error.c_str());
        } else {
          // Le JSON est supposé être un tableau d'objets
          JsonArray array = doc.as<JsonArray>();

          // Création d'un document pour conserver la dernière mesure par capteur
          DynamicJsonDocument latest(1024);
          for (JsonObject obj : array) {
            int sensorId = obj["id_capteur_actionneur"];
            float sensorValue = obj["valeur"];
            // On utilise la représentation en chaîne de l'ID comme clé
            String key = String(sensorId);
            latest[key] = sensorValue;
          }
          
          // Affichage des mesures récupérées
          JsonObject latestObj = latest.as<JsonObject>();
          for (JsonPair kv : latestObj) {
            int sensorId = atoi(kv.key().c_str());
            float sensorValue = kv.value().as<float>();
            Serial.printf("Capteur %03d : Valeur = %.2f\n", sensorId, sensorValue);
            Serial.println("Hello");
            // Contrôle de la LED intégrée selon la valeur du capteur
            // (Attention : sur ESP8266, la LED intégrée est généralement inversée)
            if (sensorValue == 1.00) {
              digitalWrite(LED_BUILTIN, LOW);  // Allume la LED
            }
            if (sensorValue == 0.00) {
              digitalWrite(LED_BUILTIN, HIGH); // Éteint la LED
            }
          }
        }
      }
    } else {
      Serial.printf("Erreur HTTP GET : %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  } else {
    Serial.println("WiFi non connecté pour GET");
  }
  
  // Attendre 5 secondes avant la prochaine itération
  delay(5000);
}
