from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import requests
import sqlite3
from datetime import datetime
import os
import webbrowser

API_KEY = "5bc3a318b0393d04039340e343ff1770"  # Remplacez par votre clé API

class MyHandler(BaseHTTPRequestHandler):
    def handle_index(self):
        # Chemin vers le fichier HTML
        html_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')

        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Envoyer la réponse HTTP avec le contenu HTML
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

        except FileNotFoundError:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = "Erreur interne du serveur : fichier HTML non trouvé."
            self.wfile.write(error_message.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = f"Erreur interne du serveur : {str(e)}"
            self.wfile.write(error_message.encode('utf-8'))
            
            
    def handle_evolution(self):
    # Extraire le paramètre 'period' (nombre de mois) ; par défaut, 12 mois
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        period = query_params.get('period', ['12'])[0]
        try:
            period_int = int(period)
        except ValueError:
            period_int = 12  # Par défaut

    # Construire la chaîne pour la fonction date de SQLite (exemple : "-6 months")
        period_str = f"-{period_int} months"

    # Connexion à la base de données et exécution de la requête SQL
        conn = sqlite3.connect("logement.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        query = """
            SELECT strftime('%Y-%m', date) AS mois,
               SUM(CASE WHEN type_facture = 'Eau' THEN valeur_consommée ELSE 0 END) AS Eau,
               SUM(CASE WHEN type_facture = 'Electricité' THEN valeur_consommée ELSE 0 END) AS Electricite,
               SUM(CASE WHEN type_facture = 'Gaz' THEN valeur_consommée ELSE 0 END) AS Gaz
            FROM Facture
            WHERE date >= date('now', ?, 'start of month')
            GROUP BY mois
            ORDER BY mois;
                """
        c.execute(query, (period_str,))
        evolution = c.fetchall()
        conn.close()

    # Préparer le tableau de données pour Google Charts
        data = [["Mois", "Eau", "Electricité", "Gaz"]]
        for row in evolution:
            data.append([row["mois"], row["Eau"], row["Electricite"], row["Gaz"]])

    # Envoyer la réponse JSON
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))



    def handle_factures(self):

    # Extraire les paramètres de la requête
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
    
    # Si le paramètre 'month' est présent, on renvoie un JSON filtré
        if 'month' in query_params:
            month = query_params['month'][0]
            # Assurez-vous que le mois est sur 2 chiffres (ex: "01", "02", …)
            if len(month) == 1:
                month = "0" + month

        # Connexion à la base de données et récupération des factures pour le mois spécifié
            conn = sqlite3.connect("logement.db")
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            query = """
                SELECT type_facture, SUM(montant) AS total
                FROM Facture
                WHERE strftime('%m', date) = ?
                GROUP BY type_facture
            """
            c.execute(query, (month,))
            factures = c.fetchall()
            conn.close()

        # Préparation des données pour le graphique
            chart_data = [["Type de Facture", "Montant"]]
            for facture in factures:
                chart_data.append([facture["type_facture"], facture["total"]])
        
        # Envoyer le JSON en réponse
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(chart_data).encode('utf-8'))
        else:
        # Pas de paramètre "month" : on renvoie la page HTML habituelle
            conn = sqlite3.connect("logement.db")
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT type_facture, SUM(montant) AS total FROM Facture GROUP BY type_facture")
            factures = c.fetchall()
            conn.close()

            chart_data = [["Type de Facture", "Montant"]]
            for facture in factures:
                chart_data.append([facture["type_facture"], facture["total"]])

            chart_data_json = json.dumps(chart_data)
            html_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'facture.html')

            try:
                with open(html_file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # Remplacer le placeholder par les données JSON
                html_content = html_content.replace('CHART_DATA_JSON', chart_data_json)

                # Envoyer la réponse HTML avec le contenu modifié
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))

            except FileNotFoundError:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                error_message = "Erreur interne du serveur : fichier HTML non trouvé."
                self.wfile.write(error_message.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                error_message = f"Erreur interne du serveur : {str(e)}"
                self.wfile.write(error_message.encode('utf-8'))



    def handle_meteo(self, scale):
        chart_data = None
        title = ""
        graph_type = "LineChart"

        if scale in ['2', '5']:
            # Utiliser l'endpoint /forecast pour 2 ou 5 jours
            url = f"http://api.openweathermap.org/data/2.5/forecast?q=Paris&appid={API_KEY}&units=metric"
            try:
                response = requests.get(url)
                response.raise_for_status()
                weather_data = response.json()

                chart_data = [["Heure et Date", "Température (°C)"]]
                count = 0
                max_count = int(scale) * 8  # 8 intervalles de 3 heures par jour

                for item in weather_data["list"]:
                    if count >= max_count:
                        break
                    dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
                    heure_et_date = f"{dt.strftime('%H:%M')}\n{dt.strftime('%d/%m')}"
                    chart_data.append([heure_et_date, item["main"]["temp"]])
                    count += 1

                title = f"Previsions Meteo pour les {scale} Prochains Jours"

            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération des données météo : {e}")
                chart_data = None

        else:
            # Échelle non reconnue
            chart_data = None

        # Chemin vers le fichier HTML
        html_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'meteo.html')

        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            if chart_data:
                chart_data_json = json.dumps(chart_data)
                # Déterminer les options dynamiques
                html_content = html_content.replace('CHART_DATA_JSON', chart_data_json)
                html_content = html_content.replace('TITLE_PLACEHOLDER', title)
                html_content = html_content.replace('GRAPH_TYPE_PLACEHOLDER', graph_type)
                # Gérer la sélection dans la barre déroulante
                selected_day = 'selected' if scale == '2' else ''
                selected_week = 'selected' if scale == '5' else ''
                html_content = html_content.replace('{{SELECTED_DAY}}', selected_day)
                html_content = html_content.replace('{{SELECTED_WEEK}}', selected_week)
            else:
                # Remplacer les placeholders même en cas d'erreur
                html_content = html_content.replace('CHART_DATA_JSON', '[]')
                html_content = html_content.replace('TITLE_PLACEHOLDER', "Prévisions Météo pour Paris")
                html_content = html_content.replace('GRAPH_TYPE_PLACEHOLDER', "LineChart")
                selected_day = 'selected' if scale == '2' else ''
                selected_week = 'selected' if scale == '5' else ''
                html_content = html_content.replace('{{SELECTED_DAY}}', selected_day)
                html_content = html_content.replace('{{SELECTED_WEEK}}', selected_week)

            # Envoyer la réponse HTTP avec le contenu HTML modifié
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

        except FileNotFoundError:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = "Erreur interne du serveur : fichier HTML non trouvé."
            self.wfile.write(error_message.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = f"Erreur interne du serveur : {str(e)}"
            self.wfile.write(error_message.encode('utf-8'))

    def handle_voir_mesure(self):
        """
        Gère la route /capteur qui affiche en temps réel les mesures de la base de données sous forme de jauges.
        """
        # Chemin vers le fichier HTML de la page "Voir mesure"
        html_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'capteur.html')

        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

        except FileNotFoundError:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = "Erreur interne du serveur : fichier HTML pour 'Voir mesure' non trouvé."
            self.wfile.write(error_message.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = f"Erreur interne du serveur : {str(e)}"
            self.wfile.write(error_message.encode('utf-8'))
            
    def handle_actionneur(self):
        # Route pour afficher la page de contrôle de l'actionneur
        html_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'actionneur.html')
        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except FileNotFoundError:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = "Erreur interne du serveur : fichier HTML pour 'Actionneur' non trouvé."
            self.wfile.write(error_message.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            error_message = f"Erreur interne du serveur : {str(e)}"
            self.wfile.write(error_message.encode('utf-8'))
            
    def handle_configuration(self):
        html_file_path = os.path.join(os.path.dirname(__file__), 'templates', 'configuration.html')
        try:
        	with open(html_file_path, 'r', encoding='utf-8') as file:
        		html_content = file.read()
        	self.send_response(200)
        	self.send_header("Content-Type", "text/html")
        	self.end_headers()
        	self.wfile.write(html_content.encode('utf-8'))
        except FileNotFoundError:
        	self.send_response(500)
        	self.send_header("Content-Type", "text/plain")
        	self.end_headers()
        	error_message = "Erreur interne du serveur : fichier configuration.html non trouvé."
        	self.wfile.write(error_message.encode('utf-8'))
        except Exception as e:
        	self.send_response(500)
        	self.send_header("Content-Type", "text/plain")
        	self.end_headers()
        	error_message = f"Erreur interne du serveur : {str(e)}"
        	self.wfile.write(error_message.encode('utf-8'))
   

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if parsed_path.path == "/":
            self.handle_index()
        elif parsed_path.path == "/factures":
            self.handle_factures()
        elif parsed_path.path == "/meteo":
            # Récupérer le paramètre 'scale', défaut à '5' si non spécifié
            scale = query_params.get('scale', ['5'])[0]
            self.handle_meteo(scale)
        elif parsed_path.path == "/capteur":
            self.handle_voir_mesure()
        elif parsed_path.path == "/actionneur":
            self.handle_actionneur() 
        elif parsed_path.path == "/get_evolution":
            self.handle_evolution()
        elif parsed_path.path == "/configuration":
            self.handle_configuration()
        elif parsed_path.path == "/get_current_temp":
            # Route pour récupérer la température actuelle de l'API
            url = f"http://api.openweathermap.org/data/2.5/weather?q=Paris&appid={API_KEY}&units=metric"
            try:
                response = requests.get(url)
                response.raise_for_status()
                weather_data = response.json()
                # Extraction de la température actuelle
                current_temp = weather_data["main"]["temp"]
                # Retourner un JSON simple
                result = {"temperature": current_temp}
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors de la récupération de la température actuelle : {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Impossible de récupérer la température actuelle"}).encode('utf-8'))

        elif parsed_path.path == "/get_factures":
            # Route pour récupérer les factures (JSON)
            conn = sqlite3.connect("logement.db")
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM Facture")
            factures = [dict(row) for row in c.fetchall()]
            conn.close()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(factures).encode('utf-8'))

        elif parsed_path.path == "/get_mesures":
            # Route pour récupérer les mesures (JSON)
            conn = sqlite3.connect("logement.db")
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM Mesure")
            mesures = [dict(row) for row in c.fetchall()]
            conn.close()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(mesures).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        if parsed_path.path == "/add_facture":
            conn = sqlite3.connect("logement.db")
            c = conn.cursor()
            query = "INSERT INTO Facture (id_logement, type_facture, date, montant, valeur_consommée) VALUES (?, ?, ?, ?, ?)"
            c.execute(query, (data["id_logement"], data["type_facture"], data["date"], data["montant"], data["valeur_consommée"]))
            conn.commit()
            conn.close()
            self.send_response(201)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Facture ajoutée avec succès!"}).encode('utf-8'))

        elif parsed_path.path == "/add_mesure":
            conn = sqlite3.connect("logement.db")
            c = conn.cursor()
            query = "INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, ?)"
            c.execute(query, (data["id_capteur_actionneur"], data["valeur"], data["date_insertion"]))
            conn.commit()
            conn.close()
            self.send_response(201)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Mesure ajoutée avec succès!"}).encode('utf-8'))
            
        elif parsed_path.path == "/delete_facture":
            data = json.loads(post_data)
            id_facture = data.get("id_facture")
            if id_facture is None:
            	self.send_response(400)
            	self.end_headers()
            	self.wfile.write(json.dumps({"error": "id_facture requis"}).encode('utf-8'))
            else:
            	conn = sqlite3.connect("logement.db")
            	c = conn.cursor()
            	c.execute("DELETE FROM Facture WHERE id_facture=?", (id_facture,))
            	conn.commit()
            	conn.close()
            	self.send_response(200)
            	self.end_headers()
            	self.wfile.write(json.dumps({"message": "Facture supprimée"}).encode('utf-8'))

        elif parsed_path.path == "/delete_mesure":
        	data = json.loads(post_data)
        	id_mesure = data.get("id_mesure")
        	if id_mesure is None:
     		   	self.send_response(400)
     		   	self.end_headers()
     		   	self.wfile.write(json.dumps({"error": "id_mesure requis"}).encode('utf-8'))
        	else:
        		try:
         		   conn = sqlite3.connect("logement.db")
         		   c = conn.cursor()
         		   c.execute("DELETE FROM Mesure WHERE id_mesure=?", (id_mesure,))
         		   conn.commit()
         		   conn.close()
         		   self.send_response(200)
         		   self.send_header("Content-Type", "application/json")
         		   self.end_headers()
         		   self.wfile.write(json.dumps({"message": "Mesure supprimée"}).encode('utf-8'))
        		except Exception as e:
         		   self.send_response(500)
         		   self.send_header("Content-Type", "application/json")
         		   self.end_headers()
         		   self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

        		
if __name__ == "__main__":
    server_address = ("0.0.0.0", 8888)
    httpd = HTTPServer(server_address, MyHandler)
    print("Serveur en cours d'exécution sur le port 8888...")
    webbrowser.open("http://localhost:8888")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        httpd.server_close()

