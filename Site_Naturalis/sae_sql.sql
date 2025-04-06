DROP TABLE IF EXISTS liste_envie,
historique,
commentaire,
note,
ligne_panier,
ligne_commande,
concerne,
declinaison_meuble,
meuble,
commande,
type_meuble,
materiau,
etat,
adresse,
utilisateur;

CREATE TABLE utilisateur(
   id_utilisateur INT AUTO_INCREMENT,
   login VARCHAR(255),
   email VARCHAR(255),
   nom_utilisateur VARCHAR(255),
   password VARCHAR(255),
   role VARCHAR(255),
   est_actif TINYINT,
   PRIMARY KEY(id_utilisateur)
);

CREATE TABLE adresse(
   id_adresse INT AUTO_INCREMENT,
   nom_adresse VARCHAR(255),
   rue VARCHAR(255),
   code_postal VARCHAR(5),
   ville VARCHAR(255),
   valide TINYINT,
   PRIMARY KEY(id_adresse)
);

CREATE TABLE etat(
   id_etat INT AUTO_INCREMENT,
   libelle_etat VARCHAR(255),
   PRIMARY KEY(id_etat)
);

CREATE TABLE materiau(
   id_materiau INT AUTO_INCREMENT,
   libelle_materiau VARCHAR(255),
   PRIMARY KEY(id_materiau)
);

CREATE TABLE type_meuble(
   id_type_meuble INT AUTO_INCREMENT,
   libelle_type_meuble VARCHAR(255),
   PRIMARY KEY(id_type_meuble)
);

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat DATETIME,
  adresse_id_livr INT NOT NULL,
   etat_id INT NOT NULL,
   utilisateur_id  INT NOT NULL,
   adresse_id_fact  INT NOT NULL,
   PRIMARY KEY(id_commande),
   FOREIGN KEY(adresse_id_livr) REFERENCES adresse(id_adresse),
   FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(adresse_id_fact) REFERENCES adresse(id_adresse)
);

CREATE TABLE meuble(
   id_meuble INT AUTO_INCREMENT,
   nom_meuble VARCHAR(255),
   disponible INT,
   prix_meuble DECIMAL(19,4),
   description_meuble VARCHAR(255),
   image_meuble VARCHAR(255),
   type_meuble_id INT NOT NULL,
   PRIMARY KEY(id_meuble),
   FOREIGN KEY(type_meuble_id) REFERENCES type_meuble(id_type_meuble)
);

CREATE TABLE declinaison_meuble(
   id_declinaison_meuble INT AUTO_INCREMENT,
   stock INT,
   prix_declinaison DECIMAL(19,4),
   image_declinaison VARCHAR(255),
   meuble_id INT NOT NULL,
   materiau_id  INT NOT NULL,
   PRIMARY KEY(id_declinaison_meuble),
   FOREIGN KEY(meuble_id) REFERENCES meuble(id_meuble),
   FOREIGN KEY(materiau_id) REFERENCES materiau(id_materiau)
);

CREATE TABLE concerne(
   utilisateur_id  INT,
   adresse_id INT,
   PRIMARY KEY(utilisateur_id, adresse_id),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(adresse_id) REFERENCES adresse(id_adresse)
);

CREATE TABLE ligne_commande(
   commande_id  INT,
   declinaison_meuble_id INT,
   quantite_lc INT,
   prix_lc DECIMAL(19,4),
   PRIMARY KEY(commande_id, declinaison_meuble_id),
   FOREIGN KEY(commande_id) REFERENCES commande(id_commande),
   FOREIGN KEY(declinaison_meuble_id) REFERENCES declinaison_meuble(id_declinaison_meuble)
);

CREATE TABLE ligne_panier(
   utilisateur_id INT,
   declinaison_meuble_id INT,
   date_ajout DATETIME,
   quantite_lp INT,
   PRIMARY KEY(utilisateur_id, declinaison_meuble_id),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(declinaison_meuble_id) REFERENCES declinaison_meuble(id_declinaison_meuble)
);

CREATE TABLE note(
   utilisateur_id INT,
   meuble_id INT,
   note DECIMAL(2,1),
   PRIMARY KEY(utilisateur_id, meuble_id),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(meuble_id) REFERENCES meuble(id_meuble)
);

CREATE TABLE commentaire(
   utilisateur_id INT,
   meuble_id INT,
   date_publication DATETIME,
   commentaire VARCHAR(255),
   valider INT,
   PRIMARY KEY(utilisateur_id, meuble_id, date_publication),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(meuble_id) REFERENCES meuble(id_meuble)
);

CREATE TABLE historique(
   utilisateur_id INT,
   meuble_id INT,
   date_consultation DATETIME,
   PRIMARY KEY(utilisateur_id, meuble_id, date_consultation),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(meuble_id) REFERENCES meuble(id_meuble)
);

CREATE TABLE liste_envie(
   utilisateur_id INT,
   meuble_id INT,
   date_update DATETIME,
   PRIMARY KEY(utilisateur_id, meuble_id, date_update),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(meuble_id) REFERENCES meuble(id_meuble)
);

INSERT INTO utilisateur (login,email,nom_utilisateur,password,`role`,est_actif) VALUES
	 ('admin','admin@admin.fr','Administrateur','pbkdf2:sha256:600000$828ij7RCZN24IWfq$3dbd14ea15999e9f5e340fe88278a45c1f41901ee6b2f56f320bf1fa6adb933d','ROLE_admin',1),
	 ('client','client@client.fr','Valentine KPOP','pbkdf2:sha256:600000$ik00jnCw52CsLSlr$9ac8f694a800bca6ee25de2ea2db9e5e0dac3f8b25b47336e8f4ef9b3de189f4','ROLE_client',1),
	 ('client2','client2@client2.fr','lamoureuse aGauthier','pbkdf2:sha256:600000$3YgdGN0QUT1jjZVN$baa9787abd4decedc328ed56d86939ce816c756ff6d94f4e4191ffc9bf357348','ROLE_client',1);

INSERT INTO adresse (nom_adresse,rue,code_postal,ville,valide) VALUES
	 ('Villa sur la cote','101 Av. du Maréchal Foch','57140','Woippy',1),
	 ('Residence des coccinelle','22 Rue du Passeur de Boulogne','92130','Issy-les-Moulineaux',1),
	 ('Quartier Louis Blanc','23 Boulevard not','92400','Courbevoie',1),
	 ('DSI Group','41 Av. du Général Leclerc','90350','Le Plessis-Robinson',1);

INSERT INTO etat (libelle_etat) VALUES
	 ('En attente'),
	 ('Expédié'),
	 ('Validé'),
	 ('Confirmé');

INSERT INTO materiau (libelle_materiau) VALUES
	 ('Sheesham massif'),
	 ('Mélaminé blanc'),
	 ('Verre'),
	 ('Rotin'),
	 ('Violet'),
	 ('Rose'),
	 ('Rouge'),
	 ('Gris'),
	 ('Vert'),
	 ('Blanc'),
	 ('Orange'),
	 ('Noir'),
	 ('Bleu'),
	 ('Bleu foncé'),
	 ('Bleu clair'),
	 ('Hêtre massif'),
	 ('Chêne massif'),
	 ('Noyer massif'),
	 ('Pin massif'),
	 ('Eucalyptus'),
	 ('Chêne clair'),
	 ('Chêne foncé');

INSERT INTO type_meuble (libelle_type_meuble) VALUES
	 ('Étagère'),
	 ('Table'),
	 ('Buffet'),
	 ('Bibliothèque'),
	 ('Vitrine'),
	 ('Chaise'),
	 ('Pouf');

INSERT INTO commande (date_achat,adresse_id_livr,etat_id,utilisateur_id,adresse_id_fact) VALUES
	 ('2025-01-01 00:00:00',2,1,2,2),
	 ('2025-01-02 00:00:00',2,1,2,2),
	 ('2025-01-03 00:00:00',4,2,3,4),
	 ('2025-01-04 00:00:00',4,3,3,4),
	 ('2025-03-03 00:00:00',2,4,2,2),
     ('2025-03-03 00:00:00',3,4,2,3);

INSERT INTO meuble (nom_meuble, disponible, prix_meuble, description_meuble, image_meuble, type_meuble_id) VALUES
    ('Etagère déstructuré',1,819.0,'Une étagère fort sympathique.','1.jpg',1),
    ('Table en sheesham',1,419.0,'Cest une table en sheesham','2.jpg',2),
    ('Buffet 2 portes 3 tiroirs',1,799.0,'Bcp de porte pr beaucoup de rangement.','3.jpg',3),
    ('Bibliothèque personnalisable',1,976.0,'Parfait pour ranger des livres.','4.jpg',4),
    ('Vitrine en verre',1,700.0,'Très belle vitrine.','13.jpg',5),
    ('Banc TV',1,345.0,'Cest pour la télé.','14.jpg',2),
    ('Vitrine figurine',1,518.0,'Magnifique vitrine','15.jpg',5),
    ('Banc',1,159.0,'Banc super qualitatif resistant','1 2.jpg',6),
    ('Bureau en bois',1,226.0,'Bureau avec un socle en rond','2 2.jpg',6),
    ('Canape pouf',1,56.0,'Canape pouf','4.webp',7),
    ('Canape zesty',1,1065.0,'Canape super qualitatif en plastique fait mains','5.png',7),
    ('Table longue',1,895.0,'Table pour graille','29.jpg',2),
    ('Table à manger',1,950.0,'Autre table toute aussi splendide','30.jpg',2),
    ('Table rustique',1,1450.0,'Elle est vieille mais rustique cest plus vendeur.','31.jpg',2),
    ('Table ronde',1,425.0,'Mais toujours pas de trace du graal... Quelquun a vu Perceval ?','32.jpg',2),
    ('Table en dur',1,2250.0,'Parce que les tables molles tiennent pas aussi bien.','33.jpg',2),
    ('chaise de jeffe',1,1400.0,'Pour se sentir comme le chef du cartel','10.webp',6),
    ('Chaise plagiste',1,750.0,'Chaise de plage','11 2.jpg',6),
    ('Etagere metal',1,75.0,'Etagere passe par tout','9.webp',1),
    ('Table basse',1,150.0,'Table design de fou','3.webp',2);

INSERT INTO declinaison_meuble (stock, prix_declinaison, image_declinaison, meuble_id, materiau_id) VALUES
    (8, 819.0, '1.jpg', 1, 1),
    (2, 419.0, '2.jpg', 2, 1),
    (3, 799.0, '3.jpg', 3, 1),
    (12, 976.0, '4.jpg', 4, 2),
    (13, 700.0, '13.jpg', 5, 3),
    (12, 345.0, '14.jpg', 6, 3),
    (2, 518.0, '15.jpg', 7, 3),
    (2, 159.0, '12.jpg', 8, 6),
    (3, 226.0, '22.jpg', 9, 6),
    (25, 56.0, '4.webp', 10, 7),
    (7, 1065.0, '5.png', 11, 8),
    (21, 895.0, '29.jpg', 12, 2),
    (2, 950.0, '30.jpg', 13, 2),
    (5, 1450.0, '31.jpg', 14, 2),
    (6, 425.0, '32.jpg', 15, 2),
    (7, 2250.0, '33.jpg', 16, 2),
    (16, 1400.0, '10.webp', 17, 6),
    (23, 750.0, '11 2.jpg', 18, 6),
    (0, 75.0, '9.webp', 19, 1),
    (12, 150.0, '3.webp', 20, 2);

INSERT INTO concerne (utilisateur_id,adresse_id) VALUES
	 (2,1),
	 (2,2),
	 (2,3),
	 (3,4);

INSERT INTO ligne_commande (commande_id, declinaison_meuble_id, quantite_lc, prix_lc) VALUES
    (1, 1, 2, 819.00),
    (1, 2, 1, 419.00),
    (2, 3, 3, 799.00),
    (3, 1, 1, 819.00),
    (4, 1, 11, 819.00),
    (4, 2, 5, 419.00),
    (4, 3, 4, 799.00),
    (4, 4, 12, 976.00),
    (4, 5, 6, 700.00),
    (4, 19, 5, 75.00),
    (4, 20, 6, 150.00),
    (5, 1, 2, 819.00),
    (5, 2, 1, 419.00),
    (5, 3, 3, 799.00),
    (5, 12, 2, 895.00),
    (5, 19, 11, 75.00),
    (5, 20, 12, 150.00),
    (6, 19, 2, 75.00),
    (6, 20, 1, 150.00),
    (6, 16, 3, 2250.00);

INSERT INTO ligne_panier (utilisateur_id, declinaison_meuble_id, date_ajout, quantite_lp) VALUES
    (1, 1, '2025-01-01 00:00:00', 2),
    (1, 3, '2025-01-01 00:00:00', 1),
    (2, 1, '2025-01-02 00:00:00', 3),
    (2, 2, '2025-01-02 00:00:00', 3),
    (3, 1, '2025-01-03 00:00:00', 1),
    (3, 12, '2025-01-04 00:00:00', 2),
    (2, 19, '2025-03-03 00:00:00', 4),
    (2, 20, '2025-03-03 00:00:00', 2);

