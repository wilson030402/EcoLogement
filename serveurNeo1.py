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
                            title: 'Repartition des Montants par Type de Facture',
                            pieHole: 0.4
                        }};
                        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
                        chart.draw(data, options);
                    }}
                </script>
            </head>
            <body>
                <h1 style="text-align: center;">Repartition des Factures</h1>
                <div id="piechart" style="width: 900px; height: 500px; margin: auto;"></div>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        # Route pour afficher la meteo (graphique sur 5 jours)
        elif parsed_path.path == "/meteo":
            url = f"http://api.openweathermap.org/data/2.5/forecast?q=Paris&appid={API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
                chart_data = [["Heure et Date", "Température (°C)"]]
                for item in weather_data["list"]:
                    dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
                    heure_et_date = f"{dt.strftime('%H:%M')}\n{dt.strftime('%d/%m')}"
                    chart_data.append([heure_et_date, item["main"]["temp"]])

                chart_data_json = json.dumps(chart_data)

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Meteo sur 5 jours (Paris)</title>
                    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                    <script type="text/javascript">
                        google.charts.load('current', {{'packages':['corechart']}});
                        google.charts.setOnLoadCallback(drawChart);

                        function drawChart() {{
                            var data = google.visualization.arrayToDataTable({chart_data_json});
                            var options = {{
                                title: 'Previsions meteo sur 5 Jours',
                                curveType: 'function',
                                legend: {{ position: 'bottom' }},
                                hAxis: {{
                                    title: 'Heure et Date',
                                    slantedText: true,
                                    slantedTextAngle: 45
                                }},
                                vAxis: {{ title: 'Température (°C)' }}
                            }};
                            var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));
                            chart.draw(data, options);
                        }}
                    </script>
                </head>
                <body>
                    <h1 style="text-align: center;">Previsions meteo pour Paris</h1>
                    <div id="curve_chart" style="width: 1500px; height: 500px;"></div>
                </body>
                </html>
                """
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_response(500)
                self.wfile.write("Erreur : Impossible de récupérer les données meteo.".encode('utf-8'))

        # Nouveau route pour récupérer la température actuelle de l'API
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
            self.wfile.write(json.dumps({"message": "Facture ajoutee avec succes!"}).encode('utf-8'))

        elif parsed_path.path == "/add_mesure":
            conn = sqlite3.connect("logement.db")
            c = conn.cursor()
            query = "INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, ?)"
            c.execute(query, (data["id_capteur_actionneur"], data["valeur"], data["date_insertion"]))
            conn.commit()
            conn.close()
            self.send_response(201)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Mesure ajoutee avec succes!"}).encode('utf-8'))

if __name__ == "__main__":
    server_address = ("0.0.0.0", 8888)
    httpd = HTTPServer(server_address, MyHandler)
    print("Serveur en cours d'exécution sur le port 8888...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        httpd.server_close()

