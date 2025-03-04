DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS meuble;
DROP TABLE IF EXISTS type_meuble;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS capacite;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS utilisateur;

CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    est_actif BOOLEAN
);

CREATE TABLE IF NOT EXISTS etat(
    id_etat INT AUTO_INCREMENT,
    libelle VARCHAR(50),
    PRIMARY KEY (id_etat)
);

CREATE TABLE IF NOT EXISTS commande (
    id_commande INT AUTO_INCREMENT,
    date_achat DATE,
    utilisateur_id INT,
    etat_id INT,
    adresse_livraison_id INT,
    adresse_facturation_id INT,
    PRIMARY KEY (id_commande),
    CONSTRAINT commande1_ibfk_1 FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    CONSTRAINT commande1_ibfk_2 FOREIGN KEY (etat_id) REFERENCES etat(id_etat) ON DELETE CASCADE,
    CONSTRAINT fk_adresse_livraison FOREIGN KEY (adresse_livraison_id) REFERENCES adresse(id_adresse),
    CONSTRAINT fk_adresse_facturation FOREIGN KEY (adresse_facturation_id) REFERENCES adresse(id_adresse)
);

CREATE TABLE IF NOT EXISTS materiau (
    id_materiau INT AUTO_INCREMENT PRIMARY KEY,
    libelle_materiau VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS type_meuble (
    id_type_meuble INT AUTO_INCREMENT PRIMARY KEY,
    libelle_type_meuble VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS meuble (
    id_meuble INT AUTO_INCREMENT PRIMARY KEY,
    nom_meuble VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    prix_meuble DECIMAL(10, 2) NOT NULL,
    couleur VARCHAR(20) NOT NULL,
    type_meuble INT NOT NULL,
    fournisseur VARCHAR(50) NOT NULL,
    marque VARCHAR(50) NOT NULL,
    photo_url VARCHAR(255) NOT NULL,
    materiau_id INT,
    utilisateur_id INT,
    CONSTRAINT meuble_ibfk_1 FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
    CONSTRAINT meuble_ibfk_2 FOREIGN KEY (materiau_id) REFERENCES materiau(id_materiau),
    CONSTRAINT meuble_ibfk_3 FOREIGN KEY (type_meuble) REFERENCES type_meuble(id_type_meuble)
);

CREATE TABLE IF NOT EXISTS ligne_panier (
    utilisateur_id INT,
    meuble_id INT,
    quantite INT,
    date_ajout DATE,
    CONSTRAINT ligne_panier_ibfk_1 FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    CONSTRAINT ligne_panier_ibfk_2 FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ligne_commande (
    commande_id INT,
    meuble_id INT,
    prix INT,
    quantite INT,
    CONSTRAINT ligne_commande_ibfk_1 FOREIGN KEY (commande_id) REFERENCES commande(id_commande) ON DELETE CASCADE,
    CONSTRAINT ligne_commande_ibfk_2 FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble) ON DELETE CASCADE
);


INSERT INTO utilisateur(id_utilisateur, login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
    'ROLE_client','client2','1');

INSERT INTO materiau (libelle_materiau)
VALUES ('BOIS'), ('METAL'), ('PLASTIQUE'), ('TISSUS');

INSERT INTO type_meuble (libelle_type_meuble)
VALUES ('TABLE'), ('CHAISE'), ('CANAPE'), ('FAUTEUIL'), ('BANQUETTE'), ('BUREAU'),('CONSOLE'), ('TABOURET');

INSERT INTO meuble (nom_meuble, description, prix_meuble, couleur, type_meuble, fournisseur, marque, photo_url, materiau_id, utilisateur_id)
VALUES
('Banquette', 'Banquette en bois de sapin coupé à la mains', 1200.00, 'brun', 5, 'BOIS&co', 'Valentine', 'banquette_bois.jpg', 1, 1),
('Bureau', 'Bureau en bois de forêt', 40.99, 'brun', 6 , 'BOIS&co', 'IKEA', 'bureau_en_bois.jpg', 1, 2),
('Bureau_Plast', 'Bureau en plastique de luxe fait maison', 3045.89, 'noir', 6, 'PLASTOC', 'Le_plastique_c_est_genial', 'bureau_en_plastoc.webp', 3, 3),
('Canape', 'Canape en tissus résistant à tout', 50.45, 'vert', 3, 'PLASTOC', 'Quartz', 'canap_en_tissus.webp', 4, 1),
('Canape_Plast', 'Canape en plastique super comfortable', 289.67, 'rose', 3, 'PLASTOC', 'Le_plastique_c_est_genial', 'canape_en_plastique.png', 3, 2),
('Chaise', 'Chaise en métal très design', 578.90, 'gris', 2, 'METALLICA', 'Valentine', 'chaise_en_metal.jpg', 2, 3),
('Chaise_Plast', 'Chaise en plastique parfait pour le camping', 9999.99, 'rouge', 2, 'PLASTOC', 'Le_plastique_c_est_genial', 'chaise_en_plastoc.jpg', 3, 1),
('Chaise_Pli', 'Chaise pliante en bois très stylax', 2.00, 'bleu', 2, 'BOIS&co', 'IKEA', 'chaise_pliante_bois.jpg', 1, 2),
('Console', 'Console en metal pour décorer tout type de pièce', 343.54, 'gris', 7, 'METALLICA', 'Quartz', 'console_metal.webp', 2, 3),
('Fauteuil_Meta', 'Fauteuil en cuir et metal design et comfortable', 567.43, 'noir', 4, 'METALLICA', 'Quartz', 'fauteuil_cuir_metal.webp', 2, 1),
('Fauteuil_Meta', 'Fauteuil full metal soudé à la main', 20.00, 'gris', 4, 'METALLICA', 'Quartz', 'fauteuil_en_metal.jpg', 2, 2),
('Table_Bass', 'Table basse en bois foncé', 7.00, 'brun', 1, 'BOIS&co', 'Valentine', 'table_basse_en_bois.jpg', 1, 3),
('Table', 'Table en bois massif magnifique', 4546.65, 'brun', 1, 'BOIS&co', 'IKEA', 'table_en_bois_massif.jpg', 1, 1),
('Table_Meta', 'Table en métal ideal pour diner a Versaille', 56.78, 'gris', 1, 'METALLICA', 'Quartz', 'table_en_metal.jpg', 2, 2),
('Tabouret', 'Tabouret pour étudiant', 1.00, 'brun', 8, 'BOIS&co', 'Valentine', 'tabouret_en_bois.jpg', 1, 3);

INSERT INTO etat(id_etat, libelle) VALUES
(1, 'En attente'),
(2, 'Expédiée'),
(3, 'Livrée');

SELECT
    meuble.nom_meuble,
    materiau.libelle_materiau AS materiau,
    meuble.description,
    meuble.prix_meuble,
    meuble.couleur,
    type_meuble.libelle_type_meuble AS type,
    meuble.fournisseur,
    meuble.marque,
    meuble.photo_url,
    meuble.utilisateur_id
FROM
    meuble
JOIN
    materiau ON meuble.materiau_id = materiau.id_materiau
JOIN
    type_meuble ON meuble.type_meuble = type_meuble.id_type_meuble;

SELECT
    nom_meuble,
    description,
    prix_meuble,
    couleur
FROM
    meuble
JOIN
    materiau ON meuble.materiau_id = materiau.id_materiau
WHERE
    materiau.libelle_materiau = 'BOIS';

SELECT
    nom_meuble,
    prix_meuble,
    couleur
FROM
    meuble
WHERE
    prix_meuble BETWEEN 9.99 AND 15;

SELECT
    nom_meuble,
    fournisseur,
    marque
FROM
    meuble
JOIN
    type_meuble ON meuble.type_meuble = type_meuble.id_type_meuble
WHERE
    type_meuble.libelle_type_meuble = 'TABLE';

SELECT
    nom_meuble,
    prix_meuble,
    description,
    marque
FROM
    meuble
ORDER BY
    prix_meuble DESC;

SELECT
    type_meuble.libelle_type_meuble AS type,
    COUNT(meuble.id_meuble) AS nombre_meuble
FROM
    meuble
JOIN
    type_meuble ON meuble.type_meuble = type_meuble.id_type_meuble
GROUP BY
    type_meuble.libelle_type_meuble;

SELECT
    nom_meuble,
    materiau.libelle_materiau AS materiau,
    type_meuble.libelle_type_meuble AS type,
    prix_meuble
FROM
    meuble
JOIN
    materiau ON meuble.materiau_id = materiau.id_materiau
JOIN
    type_meuble ON meuble.type_meuble = type_meuble.id_type_meuble
ORDER BY
    materiau.libelle_materiau;

SELECT
    nom_meuble,
    description,
    prix_meuble,
    couleur
FROM
    meuble
WHERE
    marque = 'Valentine';

