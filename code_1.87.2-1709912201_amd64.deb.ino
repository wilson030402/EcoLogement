#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// Remplacez ces valeurs par vos informations personnelles
const char* ssid       = "Livebox-215E";
const char* password   = "sZfz35nXn5h3L2rnVN";

// Adresse IP du serveur où tourne votre code Python et le port utilisé (ici 8888)
const char* serverIP   = "192.168.1.29";  // par exemple
const int   serverPort = 8888;

String serverURL = String("http://") + serverIP + ":" + String(serverPort) + "/get_mesures";

void setup() {
  Serial.begin(115200);
  delay(100);
  pinMode(LED_BUILTIN, OUTPUT);
  // Connexion au WiFi
  Serial.print("Connexion au WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connecté");
  Serial.print("Adresse IP : ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    WiFiClient client;
    // Initialiser la requête vers le serveur en utilisant le WiFiClient (nouvelle API)
    http.begin(client, serverURL);
    int httpCode = http.GET();
    if (httpCode > 0) {
      // Si la requête a réussi, lire la réponse
      String payload = http.getString();
      Serial.println("Réponse du serveur :");
      Serial.println(payload);

      // Définir une capacité adaptée pour le document JSON
      const size_t capacity = JSON_ARRAY_SIZE(20) + 20 * JSON_OBJECT_SIZE(4);
      DynamicJsonDocument doc(capacity);

      // Désérialiser le JSON
      DeserializationError error = deserializeJson(doc, payload);
      if (error) {
        Serial.print("Erreur de désérialisation JSON : ");
        Serial.println(error.c_str());
      } else {
        // Le JSON est supposé être un tableau d'objets
        JsonArray array = doc.as<JsonArray>();

        // Créer un document pour stocker la valeur la plus récente de chaque capteur.
        // Ici, on utilise les clés (string) correspondant aux id du capteur.
        DynamicJsonDocument latest(1024);
        
        // Pour chaque mesure, on écrase la valeur précédente pour le même capteur.
        for (JsonObject obj : array) {
          int sensorId = obj["id_capteur_actionneur"];
          float sensorValue = obj["valeur"];
          // Utiliser la représentation en chaîne de l'id comme clé
          String key = String(sensorId);
          latest[key] = sensorValue;
        }

        // Itérer sur les paires (clé/valeur) du document "latest" et afficher le résultat.
        JsonObject latestObj = latest.as<JsonObject>();
        for (JsonPair kv : latestObj) {
          // Convertir la clé en entier
          int sensorId = atoi(kv.key().c_str());
          float sensorValue = kv.value().as<float>();
          // Afficher l'id du capteur sur 3 chiffres et sa valeur formatée sur 2 décimales
          Serial.printf("Capteur %03d : Valeur = %.2f\n", sensorId, sensorValue);
          if (sensorValue == 1.00) {
              digitalWrite(LED_BUILTIN, LOW);
          }

          if (sensorValue == 0.00) {
              digitalWrite(LED_BUILTIN, HIGH);
          }
        }
      }
    } else {
      Serial.printf("Erreur HTTP GET : %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  } else {
    Serial.println("WiFi non connecté");
  }

  // Attendre 5 secondes avant la prochaine lecture
  delay(5000);
}
