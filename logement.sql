--RANGANATHAN Yeogeuch
-- Détruire les tables existantes dans la base de données
-- Les tables sont supprimées dans un ordre spécifique pour éviter les erreurs de contrainte de clé étrangère

DROP TABLE IF EXISTS Mesure;
DROP TABLE IF EXISTS Facture;
DROP TABLE IF EXISTS CapteurActionneur;
DROP TABLE IF EXISTS TypeCapteurActionneur;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Logement;

-- Fin de la destruction des tables

-- Création des tables pour le projet "Logement éco-responsable"

-- Table Logement
-- Cette table stocke les informations principales sur chaque logement.
CREATE TABLE IF NOT EXISTS Logement (
    id_logement INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique du logement
    adresse TEXT NOT NULL,                        -- Adresse du logement
    telephone INTEGER,                            -- Numéro de téléphone (format numérique uniquement)
    adresse_ip TEXT,                              -- Adresse IP du logement
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Date d'insertion dans la base
);

-- Table Pièce
-- Cette table représente les pièces d’un logement. Chaque pièce est associée à un logement.
CREATE TABLE IF NOT EXISTS Piece (
    id_piece INTEGER PRIMARY KEY AUTOINCREMENT,   -- Identifiant unique de la pièce
    nom_piece TEXT NOT NULL,                      -- Nom de la pièce
    coordonnees TEXT,                             -- Coordonnées 3D de la pièce
    id_logement INTEGER NOT NULL,                 -- Référence au logement associé
    FOREIGN KEY (id_logement) REFERENCES Logement (id_logement) -- Clé étrangère vers Logement
);

-- Table TypeCapteurActionneur
-- Cette table stocke les types de capteurs/actionneurs (ex: température, électricité).
-- Table TypeCapteurActionneur
CREATE TABLE IF NOT EXISTS TypeCapteurActionneur (
    id_type INTEGER PRIMARY KEY AUTOINCREMENT,    -- Identifiant unique du type
    nom_type TEXT NOT NULL,                       -- Nom du type
    unite_mesure TEXT,                            -- Unité de mesure (ex: °C, kWh)
    plage_precision TEXT,                         -- Plage de précision du capteur/actionneur
    description TEXT                              -- Description supplémentaire
);

-- Table CapteurActionneur
-- Cette table représente les capteurs/actionneurs dans les pièces d’un logement.
CREATE TABLE IF NOT EXISTS CapteurActionneur (
    id_capteur_actionneur INTEGER PRIMARY KEY AUTOINCREMENT, -- Identifiant unique
    id_piece INTEGER NOT NULL,                              -- Référence à la pièce associée
    id_type INTEGER NOT NULL,                               -- Référence au type de capteur/actionneur
    ref_commerciale TEXT,                                   -- Référence commerciale
    port_communication INTEGER NOT NULL,                   -- Port de communication avec le serveur
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Date d’insertion dans la base
    FOREIGN KEY (id_piece) REFERENCES Piece (id_piece),     -- Clé étrangère vers Piece
    FOREIGN KEY (id_type) REFERENCES TypeCapteurActionneur (id_type) -- Clé étrangère vers TypeCapteurActionneur
);

-- Table Mesure
-- Cette table stocke les mesures enregistrées par les capteurs/actionneurs.
CREATE TABLE IF NOT EXISTS Mesure (
    id_mesure INTEGER PRIMARY KEY AUTOINCREMENT,    -- Identifiant unique de la mesure
    id_capteur_actionneur INTEGER NOT NULL,         -- Référence au capteur/actionneur associé
    valeur REAL NOT NULL,                           -- Valeur mesurée
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Date de la mesure
    FOREIGN KEY (id_capteur_actionneur) REFERENCES CapteurActionneur (id_capteur_actionneur) -- Clé étrangère vers CapteurActionneur
);

-- Table Facture
-- Cette table stocke les factures associées à un logement (eau, électricité, etc.).
CREATE TABLE IF NOT EXISTS Facture (
    id_facture INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique de la facture
    id_logement INTEGER NOT NULL,                 -- Référence au logement associé
    type_facture TEXT NOT NULL,                   -- Type de facture (eau, électricité, déchets)
    date DATE NOT NULL,                           -- Date de la facture
    montant REAL NOT NULL,                        -- Montant de la facture
    valeur_consommée REAL NOT NULL,               -- Valeur consommée (ex: kWh, litres)
    FOREIGN KEY (id_logement) REFERENCES Logement (id_logement) -- Clé étrangère vers Logement
);

-- Insertion d'un logement dans la table Logement
-- Exemple d'un logement fictif
INSERT INTO Logement (adresse, telephone, adresse_ip)
VALUES ('4 Place Jussieu, Paris', 1234567890, '192.168.1.1');

-- Récupération de l'identifiant du logement inséré
-- Supposons que l'identifiant du logement inséré est 1 (id_logement = 1)

-- Insertion des 4 pièces associées à ce logement
-- Chaque pièce est liée au logement via id_logement
INSERT INTO Piece (nom_piece, coordonnees, id_logement)
VALUES 
    ('Salon', '(0,0,0)', 1),
    ('Cuisine', '(0,1,0)', 1),
    ('Chambre', '(1,0,0)', 1),
    ('douche', '(1,1,1)', 1);

-- Fin de l'insertion du logement et de ses pièces

-- Insertion de 4 types de capteurs/actionneurs dans la table TypeCapteurActionneur
-- Ces types sont définis avec un nom, une unité de mesure et une plage de précision

INSERT INTO TypeCapteurActionneur (nom_type, unite_mesure, plage_precision, description)
VALUES
    ('Température', '°C', '-40 à 125', 'Capteur de température pour mesurer l''environnement'),
    ('Humidité', '%', '0 à 100', 'Capteur pour mesurer l''humidité relative'),
    ('Luminosité', 'lux', '0 à 100000', 'Capteur pour mesurer l''intensité lumineuse'),
    ('Consommation électrique', 'kWh', '0 à 9999', 'Capteur pour surveiller la consommation d''électricité');

-- Fin de l'insertion des types de capteurs/actionneurs

-- Insertion de 2 capteurs/actionneurs dans la table CapteurActionneur
-- Chaque capteur/actionneur est associé à une pièce et à un type

INSERT INTO CapteurActionneur (id_piece, id_type, ref_commerciale, port_communication, date_insertion)
VALUES
    (1, 1, 'CTemp123', 8080, CURRENT_TIMESTAMP), -- Capteur de température dans la pièce 1
    (2, 2, 'CHum456', 8081, CURRENT_TIMESTAMP);  -- Capteur d'humidité dans la pièce 2

-- Fin de l'insertion des capteurs/actionneurs

-- Insertion de mesures pour les capteurs/actionneurs
-- Ces mesures sont associées à des capteurs/actionneurs déjà présents dans la base

-- Mesures pour le capteur/actionneur avec id_capteur_actionneur = 1 (Capteur de température)
INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion)
VALUES
    (1, 22.5, CURRENT_TIMESTAMP), -- Température mesurée à 22.5°C
    (1, 23.1, CURRENT_TIMESTAMP); -- Température mesurée à 23.1°C

