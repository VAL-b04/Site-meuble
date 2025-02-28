DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS concerne;
DROP TABLE IF EXISTS declinaison_meuble;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS meuble;
DROP TABLE IF EXISTS adresse;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS type_meuble;
DROP TABLE IF EXISTS materiau;



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

CREATE TABLE type_meuble(
   id_type_meuble INT AUTO_INCREMENT,
   libelle_type_meuble VARCHAR(255),
   PRIMARY KEY(id_type_meuble)
);


CREATE TABLE materiau(
   id_materiau INT AUTO_INCREMENT,
   libelle_materiau VARCHAR(255),
   PRIMARY KEY(id_materiau)
);

CREATE TABLE etat(
   id_etat INT AUTO_INCREMENT,
   libelle_etat VARCHAR(255),
   PRIMARY KEY(id_etat)
);

CREATE TABLE IF NOT EXISTS meuble (
    id_meuble INT AUTO_INCREMENT,
    id_type INT,
    id_materiau INT,
    nom_meuble VARCHAR(255),
    largeur DECIMAL(15,2),
    hauteur DECIMAL(15,2),
    prix_meuble DECIMAL(15,2),
    fournisseur VARCHAR(255),
    marque VARCHAR(255),
    image VARCHAR(255),
    stock INT,
    description VARCHAR(255),
    PRIMARY KEY (id_meuble),
    FOREIGN KEY (id_type) REFERENCES type_meuble(id_type_meuble),
    FOREIGN KEY (id_materiau) REFERENCES materiau(id_materiau)
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

CREATE TABLE commande(
   id_commande INT AUTO_INCREMENT,
   date_achat DATE,
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

CREATE TABLE concerne(
   utilisateur_id  INT,
   adresse_id INT,
   PRIMARY KEY(utilisateur_id, adresse_id),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(adresse_id) REFERENCES adresse(id_adresse)
);

CREATE TABLE ligne_panier(
   utilisateur_id INT,
   declinaison_meuble_id INT,
   date_ajout DATE,
   quantite_lp INT,
   PRIMARY KEY(utilisateur_id, declinaison_meuble_id),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(declinaison_meuble_id) REFERENCES declinaison_meuble(id_declinaison_meuble)
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


INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom_utilisateur,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'scrypt:32768:8:1$irSP6dJEjy1yXof2$56295be51bb989f467598b63ba6022405139656d6609df8a71768d42738995a21605c9acbac42058790d30fd3adaaec56df272d24bed8385e66229c81e71a4f4',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'scrypt:32768:8:1$iFP1d8bdBmhW6Sgc$7950bf6d2336d6c9387fb610ddaec958469d42003fdff6f8cf5a39cf37301195d2e5cad195e6f588b3644d2a9116fa1636eb400b0cb5537603035d9016c15910',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'scrypt:32768:8:1$l3UTNxiLZGuBKGkg$ae3af0d19f0d16d4a495aa633a1cd31ac5ae18f98a06ace037c0f4fb228ed86a2b6abc64262316d0dac936eb72a67ae82cd4d4e4847ee0fb0b19686ee31194b3',
    'ROLE_client','client2','1');

INSERT INTO adresse (nom_adresse,rue,code_postal,ville,valide) VALUES
	 ('Crêperie les Tonnelles','101 Av. du Maréchal Foch','93210','Saint-Cloud',1),
	 ('Residhome Paris Issy-les-Moulineaux','22-24 Rue du Passeur de Boulogne','92130','Issy-les-Moulineaux',1),
	 ('Jack Séparou Maison','Boulevard not','06401','Cdds',1),
	 ('DSI Group','41 Av. du Général Leclerc','90350','Le Plessis-Robinson',1);

INSERT INTO type_meuble( libelle_type_meuble) VALUES
( 'Table'),
( 'Chaise'),
( 'Canapé');


INSERT INTO materiau(libelle_materiau) VALUES
( 'Bois'),
( 'Métal'),
( 'Plastique');


INSERT INTO etat( libelle_etat) VALUES
( 'En attente'),
( 'Expédiée'),
( 'Livrée');


INSERT INTO meuble ( id_type, id_materiau, nom_meuble, largeur, hauteur, prix_meuble, fournisseur, marque, image, stock, description) VALUES
( 1, 1, 'Table en bois massif', 150.00, 75.00, 200.00, 'Eminza', 'Valentine', 'table_en_bois_massif.jpg', 5, 'table en bois massif de l au-dela'),
( 2, 2, 'Chaise en métal', 45.00, 90.00, 80.00, 'Ikea', 'Quartz', 'chaise_en_metal.jpg', 8, 'chaise en métal de mars'),
( 3, 3, 'Canapé en plastique', 200.00, 85.00, 350.00, 'Pipo', 'Passion Meuble', 'canape_plastiq.jpg', 9, 'canape en plastique très confortable'),
( 1, 1, 'Bureau en bois', 120.00, 75.00, 180.00, 'Eminza', 'Valentine', 'bureau_en_bois.jpg', 8, 'bureau en bois de chene premium'),
( 2, 1, 'Tabouret en bois', 30.00, 50.00, 50.00, 'Moldue', 'Ontop', 'tabouret_en_bois.jpg', 4, 'tabouret en bois très qualitatif'),
( 1, 2, 'Table en métal', 140.00, 78.00, 250.00, 'Eminza', 'Quartz', 'table_en_metal.jpg', 3, 'table en métal précieux'),
( 3, 2, 'Fauteuil en métal', 90.00, 100.00, 150.00, 'Pipo', 'Passion Meuble', 'fauteuil_en_metal.jpg', 1, 'fauteuil en metal de luxe'),
( 3, 3, 'Canapé en tissu', 220.00, 95.00, 400.00, 'Moldue', 'Ontop', 'canap_en_tissus.webp', 4, 'canape en tissus cousu à la main'),
( 2, 3, 'Chaise en plastique', 50.00, 95.00, 70.00, 'Ikea', 'Valentine', 'chaise_en_plastoc.jpg', 3, 'chaise en plastique premier prix'),
( 1, 3, 'Bureau en plastique', 110.00, 75.00, 120.00, 'Cadecap', 'En place', 'bureau_plast.jpeg', 2, 'bureau en plastique'),
( 1, 1, 'Table basse en bois', 100.00, 45.00, 100.00, 'Ikea', 'Valentine', 'table_basse_en_bois.jpg', 7, 'table basse en bois de bouleau'),
( 2, 1, 'Chaise pliante en bois', 40.00, 85.00, 60.00, 'Eminza', 'Quartz', 'chaise_pliante_bois.jpg', 5, 'chaise pliante en bois de sapin'),
( 3, 1, 'Banquette en bois', 180.00, 80.00, 300.00, 'Moldue', 'Ontop', 'banquette_bois.jpg', 4, 'banquette en bois d accacia'),
( 3, 2, 'Fauteuil en cuir et métal', 95.00, 110.00, 500.00, 'Cadecap', 'En place', 'fauteuil_cuir_metal.webp', 11, 'fauteuil en cuir et metal imitation mafieu'),
( 1, 2, 'Console en métal', 130.00, 70.00, 320.00, 'ConsossionMeuble', 'Quartz', 'console_metal.webp', 15, 'console en metal pour travailler en toute tranquilité');

/*ALTER TABLE declinaison_meuble
DROP FOREIGN KEY declinaison_meuble_ibfk_1,
DROP FOREIGN KEY declinaison_meuble_ibfk_2;*/

INSERT INTO declinaison_meuble (stock, prix_declinaison, image_declinaison, meuble_id, materiau_id) VALUES
    -- Déclinaisons pour la Table en bois massif
    (5, 200.00, 'table_en_bois_massif.jpg', 1, 1),
    (3, 210.00, 'table_en_bois_massif.jpg', 1, 2),
    (2, 195.00, 'table_en_bois_massif.jpg', 1, 3),

    -- Déclinaisons pour la Chaise en métal
    (8, 80.00, 'chaise_en_metal.jpg', 2, 2),
    (4, 85.00, 'chaise_en_metal.jpg', 2, 1),
    (3, 78.00, 'chaise_en_metal.jpg', 2, 3),

    -- Déclinaisons pour le Canapé en plastique
    (9, 350.00, 'canape_plastiq.jpg', 3, 3),
    (6, 340.00, 'canape_plastiq.jpg', 3, 2),
    (3, 360.00, 'canape_plastiq.jpg', 3, 1),

    -- Déclinaisons pour le Bureau en bois
    (8, 180.00, 'bureau_en_bois.jpg', 4, 1),
    (4, 175.00, 'bureau_en_bois.jpg', 4, 2),
    (2, 185.00, 'bureau_en_bois.jpg', 4, 3),

    -- Déclinaisons pour le Tabouret en bois
    (4, 50.00, 'tabouret_en_bois.jpg', 5, 1),
    (2, 55.00, 'tabouret_en_bois.jpg', 5, 2),
    (1, 48.00, 'tabouret_en_bois.jpg', 5, 3),

    -- Déclinaisons pour la Table en métal
    (3, 250.00, 'table_en_metal.jpg', 6, 2),
    (2, 260.00, 'table_en_metal.jpg', 6, 1),
    (1, 245.00, 'table_en_metal.jpg', 6, 3),

    -- Déclinaisons pour le Fauteuil en métal
    (1, 150, 'fauteuil_en_metal.jpg', 7, 2),
    (2, 155, 'fauteuil_en_metal.jpg', 7, 1),
    (1, 148, 'fauteuil_en_metal.jpg', 7, 3),

    -- Déclinaisons pour le Canapé en tissu
    (4, 400.00, 'canap_en_tissus.webp', 8, 3),
    (3, 390.00, 'canap_en_tissus.webp', 8, 2),
    (2, 410.00, 'canap_en_tissus.webp', 8, 1),

    -- Déclinaisons pour la Chaise en plastique
    (3, 70.00, 'chaise_en_plastoc.jpg', 9, 3),
    (2, 75.00, 'chaise_en_plastoc.jpg', 9, 2),
    (1, 65.00, 'chaise_en_plastoc.jpg', 9, 1),

    -- Déclinaisons pour le Bureau en plastique
    (2, 120.00, 'bureau_plast.jpeg', 10, 3),
    (1, 130.00, 'bureau_plast.jpeg', 10, 2),
    (1, 110.00, 'bureau_plast.jpeg', 10, 1),

    -- Déclinaisons pour la Table basse en bois
    (7, 100.00, 'table_basse_en_bois.jpg', 11, 1),
    (5, 105.00, 'table_basse_en_bois.jpg', 11, 2),
    (3, 98.00, 'table_basse_en_bois.jpg', 11, 3),

    -- Déclinaisons pour la Chaise pliante en bois
    (5, 60.00, 'chaise_pliante_bois.jpg', 12, 1),
    (3, 65.00, 'chaise_pliante_bois.jpg', 12, 2),
    (2, 58.00, 'chaise_pliante_bois.jpg', 12, 3),

    -- Déclinaisons pour la Banquette en bois
    (4, 300.00, 'banquette_bois.jpg', 13, 1),
    (2, 310.00, 'banquette_bois.jpg', 13, 2),
    (1, 290.00, 'banquette_bois.jpg', 13, 3),

    -- Déclinaisons pour le Fauteuil en cuir et métal
    (11, 500.00, 'fauteuil_cuir_metal.webp', 14, 2),
    (7, 520.00, 'fauteuil_cuir_metal.webp', 14, 1),
    (5, 490.00, 'fauteuil_cuir_metal.webp', 14, 3),

    -- Déclinaisons pour la Console en métal
    (15, 180.00, 'console_metal.webp', 15, 2),
    (10, 190.00, 'console_metal.webp', 15, 1),
    (7, 175.00, 'console_metal.webp', 15, 3);




INSERT INTO commande(date_achat, etat_id, utilisateur_id, adresse_id_livr, adresse_id_fact) VALUES
( '2025-01-01', 1, 2,1,1),
( '2025-01-15', 2, 3,2,2),
( '2025-02-01', 3, 2,3,3);

INSERT INTO concerne (utilisateur_id,adresse_id) VALUES
	 (1,1),
	 (2,2),
	 (2,3),
	 (3,4);


INSERT INTO ligne_panier(utilisateur_id, declinaison_meuble_id, quantite_lp, date_ajout) VALUES
(2, 1, 2, '2025-01-05'),
(3, 2, 1, '2025-01-10'),
(2, 3, 1, '2025-01-12');


INSERT INTO ligne_commande(commande_id, declinaison_meuble_id, prix_lc, quantite_lc) VALUES
(1, 1, 150.00, 2),
(2, 2, 75.00, 1),
(3, 3, 300.00, 1);

