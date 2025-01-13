from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import json
import requests
import sqlite3
from datetime import datetime

API_KEY = "5bc3a318b0393d04039340e343ff1770"  # Remplacez par votre clé API

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # Route pour afficher le camembert des factures
        if parsed_path.path == "/factures":
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

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Camembert des Factures</title>
                <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                <script type="text/javascript">
                    google.charts.load('current', {{'packages':['corechart']}});
                    google.charts.setOnLoadCallback(drawChart);

                    function drawChart() {{
                        var data = google.visualization.arrayToDataTable({chart_data_json});
                        var options = {{
                            title: 'Répartition des Montants par Type de Facture',
                            pieHole: 0.4
                        }};
                        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
                        chart.draw(data, options);
                    }}
                </script>
            </head>
            <body>
                <h1 style="text-align: center;">Répartition des Factures</h1>
                <div id="piechart" style="width: 900px; height: 500px; margin: auto;"></div>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        # Route modifiée pour afficher la météo avec une barre déroulante
        elif parsed_path.path == "/meteo":
            # Récupérer le paramètre 'scale', défaut à '5' si non spécifié
            scale = query_params.get('scale', ['5'])[0]

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

                    title = f"Prévisions Météo pour les {scale} Prochains Jours"

                except requests.exceptions.RequestException as e:
                    print(f"Erreur lors de la récupération des données météo : {e}")
                    chart_data = None

            else:
                # Échelle non reconnue
                chart_data = None

            # Préparer le graphique si les données sont disponibles
            if chart_data:
                chart_data_json = json.dumps(chart_data)

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Météo pour Paris</title>
                    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                    <script type="text/javascript">
                        google.charts.load('current', {{'packages':['corechart']}});
                        google.charts.setOnLoadCallback(drawChart);

                        function drawChart() {{
                            var data = google.visualization.arrayToDataTable({chart_data_json});
                            var options = {{
                                title: '{title}',
                                curveType: 'function',
                                legend: {{ position: 'bottom' }},
                                hAxis: {{
                                    title: 'Heure et Date',
                                    slantedText: true,
                                    slantedTextAngle: 45
                                }},
                                vAxis: {{ title: 'Température (°C)' }}
                            }};
                            var chart = new google.visualization.{graph_type}(document.getElementById('curve_chart'));
                            chart.draw(data, options);
                        }}
                    </script>
                </head>
                <body>
                    <h1 style="text-align: center;">Prévisions Météo pour Paris</h1>
                    <div style="text-align: center; margin-bottom: 20px;">
                        <label for="scale">Choisissez l'échelle de temps : </label>
                        <select id="scale" name="scale" onchange="changeScale()">
                            <option value="2" {"selected" if scale == "2" else ""}>2 Jours</option>
                            <option value="5" {"selected" if scale == "5" else ""}>5 Jours</option>
                        </select>
                    </div>
                    <div id="curve_chart" style="width: 1500px; height: 500px; margin: auto;"></div>
                    <script type="text/javascript">
                        function changeScale() {{
                            var scale = document.getElementById('scale').value;
                            window.location.href = "/meteo?scale=" + scale;
                        }}
                    </script>
                </body>
                </html>
                """
            else:
                # Si aucune donnée disponible (par exemple, pour des erreurs ou des échelles non supportées)
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Météo pour Paris</title>
                </head>
                <body>
                    <h1 style="text-align: center;">Prévisions Météo pour Paris</h1>
                    <div style="text-align: center; margin-bottom: 20px;">
                        <label for="scale">Choisissez l'échelle de temps : </label>
                        <select id="scale" name="scale" onchange="changeScale()">
                            <option value="2" {"selected" if scale == "2" else ""}>2 Jours</option>
                            <option value="5" {"selected" if scale == "5" else ""}>5 Jours</option>
                        </select>
                    </div>
                    <p style="text-align: center;">Données météo pour cette échelle de temps ne sont pas disponibles.</p>
                    <script type="text/javascript">
                        function changeScale() {{
                            var scale = document.getElementById('scale').value;
                            window.location.href = "/meteo?scale=" + scale;
                        }}
                    </script>
                </body>
                </html>
                """

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        # Route pour récupérer la température actuelle de l'API
        elif parsed_path.path == "/get_current_temp":
            url = f"http://api.openweathermap.org/data/2.5/weather?q=Paris&appid={API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
                # Extraction de la température actuelle
                current_temp = weather_data["main"]["temp"]
                # Retourner un JSON simple
                result = {"temperature": current_temp}
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Impossible de récupérer la température actuelle"}).encode('utf-8'))

        # Route pour récupérer les factures (JSON)
        elif parsed_path.path == "/get_factures":
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

        # Route pour récupérer les mesures (JSON)
        elif parsed_path.path == "/get_mesures":
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

if __name__ == "__main__":
    server_address = ("0.0.0.0", 8888)
    httpd = HTTPServer(server_address, MyHandler)
    print("Serveur en cours d'exécution sur le port 8888...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        httpd.server_close()

