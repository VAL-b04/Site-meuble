DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS meuble;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS type_meuble;
DROP TABLE IF EXISTS materiau;



CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur INT AUTO_INCREMENT,
    login VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    est_actif TINYINT(1),
    PRIMARY KEY (id_utilisateur)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS type_meuble (
    id_type INT AUTO_INCREMENT,
    libelle_type VARCHAR(255),
    PRIMARY KEY (id_type)
);

CREATE TABLE IF NOT EXISTS materiau (
    id_materiau INT AUTO_INCREMENT,
    libelle_materiau VARCHAR(255),
    PRIMARY KEY (id_materiau)
);

CREATE TABLE IF NOT EXISTS etat (
   id_etat INT AUTO_INCREMENT,
   libelle_etat VARCHAR(255),
   PRIMARY KEY (id_etat)
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
    PRIMARY KEY (id_meuble),
    FOREIGN KEY (id_type) REFERENCES type_meuble(id_type),
    FOREIGN KEY (id_materiau) REFERENCES materiau(id_materiau)
);

CREATE TABLE IF NOT EXISTS commande (
    id_commande INT AUTO_INCREMENT,
    data_achat DATE,
    etat_id INT,
    utilisateur_id INT,
    PRIMARY KEY (id_commande),
    FOREIGN KEY (etat_id) REFERENCES etat(id_etat),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE IF NOT EXISTS ligne_panier (
    id_utilisateur INT,
    id_meuble INT,
    quantite INT,
    date_ajout DATE,
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (id_meuble) REFERENCES meuble(id_meuble)
);

CREATE TABLE IF NOT EXISTS ligne_commande (
    id_commande INT,
    id_meuble INT,
    prix DECIMAL(15,2),
    quantite INT,
    FOREIGN KEY (id_commande) REFERENCES commande(id_commande),
    FOREIGN KEY (id_meuble) REFERENCES meuble(id_meuble)
);


INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'sha256$dPL3oH9ug1wjJqva$2b341da75a4257607c841eb0dbbacb76e780f4015f0499bb1a164de2a893fdbf',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'sha256$1GAmexw1DkXqlTKK$31d359e9adeea1154f24491edaa55000ee248f290b49b7420ced542c1bf4cf7d',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'sha256$MjhdGuDELhI82lKY$2161be4a68a9f236a27781a7f981a531d11fdc50e4112d912a7754de2dfa0422',
    'ROLE_client','client2','1');

INSERT INTO type_meuble(id_type, libelle_type) VALUES
(1, 'Table'),
(2, 'Chaise'),
(3, 'Canapé');


INSERT INTO materiau(id_materiau, libelle_materiau) VALUES
(1, 'Bois'),
(2, 'Métal'),
(3, 'Plastique');


INSERT INTO etat(id_etat, libelle_etat) VALUES
(1, 'En attente'),
(2, 'Expédiée'),
(3, 'Livrée');


INSERT INTO meuble(id_meuble, id_type, id_materiau, nom_meuble, largeur, hauteur, prix_meuble, fournisseur, marque) VALUES
(1, 1, 1, 'Table en bois massif', 150.00, 75.00, 200.00, 'Fournisseur A', 'Marque X'),
(2, 2, 2, 'Chaise en métal', 45.00, 90.00, 80.00, 'Fournisseur B', 'Marque Y'),
(3, 3, 3, 'Canapé en plastique', 200.00, 85.00, 350.00, 'Fournisseur C', 'Marque Z'),
(4, 1, 1, 'Bureau en bois', 120.00, 75.00, 180.00, 'Fournisseur A', 'Marque X'),
(5, 2, 1, 'Tabouret en bois', 30.00, 50.00, 50.00, 'Fournisseur D', 'Marque W'),
(6, 1, 2, 'Table en métal', 140.00, 78.00, 250.00, 'Fournisseur B', 'Marque Y'),
(7, 3, 2, 'Fauteuil en métal', 90.00, 100.00, 150.00, 'Fournisseur C', 'Marque Z'),
(8, 3, 3, 'Canapé en tissu', 220.00, 95.00, 400.00, 'Fournisseur D', 'Marque W'),
(9, 2, 3, 'Chaise en plastique', 50.00, 95.00, 70.00, 'Fournisseur A', 'Marque X'),
(10, 1, 3, 'Bureau en plastique', 110.00, 75.00, 120.00, 'Fournisseur E', 'Marque V'),
(11, 1, 1, 'Table basse en bois', 100.00, 45.00, 100.00, 'Fournisseur A', 'Marque X'),
(12, 2, 1, 'Chaise pliante en bois', 40.00, 85.00, 60.00, 'Fournisseur B', 'Marque Y'),
(13, 3, 1, 'Banquette en bois', 180.00, 80.00, 300.00, 'Fournisseur D', 'Marque W'),
(14, 3, 2, 'Fauteuil en cuir et métal', 95.00, 110.00, 500.00, 'Fournisseur E', 'Marque V'),
(15, 1, 2, 'Console en métal', 130.00, 70.00, 180.00, 'Fournisseur C', 'Marque Z');



INSERT INTO commande(id_commande, data_achat, etat_id, utilisateur_id) VALUES
(1, '2025-01-01', 1, 2),
(2, '2025-01-15', 2, 3),
(3, '2025-02-01', 3, 2);


INSERT INTO ligne_panier(id_utilisateur, id_meuble, quantite, date_ajout) VALUES
(2, 1, 2, '2025-01-05'),
(3, 2, 1, '2025-01-10'),
(2, 3, 1, '2025-01-12');


INSERT INTO ligne_commande(id_commande, id_meuble, prix, quantite) VALUES
(1, 1, 150.00, 2),
(2, 2, 75.00, 1),
(3, 3, 300.00, 1);
