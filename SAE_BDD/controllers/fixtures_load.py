#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db
from werkzeug.security import generate_password_hash

fixtures_load = Blueprint('fixtures_load', __name__,
                          template_folder='templates')

@fixtures_load.route('/base/init')
def fct_fixtures_load():
    mycursor = get_db().cursor()

    mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    sql = '''DROP TABLE IF EXISTS utilisateur, type_meuble, etat, meuble, commande, ligne_commande, ligne_panier, adresse, liste_envies, historique, declinaison, commentaire'''
    mycursor.execute(sql)

    mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    sql = '''
    CREATE TABLE utilisateur(
        id_utilisateur INT AUTO_INCREMENT PRIMARY KEY,
        login VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        nom VARCHAR(255),
        est_actif TINYINT(1) DEFAULT 1
    ) DEFAULT CHARSET utf8;  
    '''
    mycursor.execute(sql)

    admin_password = generate_password_hash('admin', method='pbkdf2:sha256')
    client_password = generate_password_hash('client', method='pbkdf2:sha256')
    client2_password = generate_password_hash('client2', method='pbkdf2:sha256')

    sql = ''' 
    INSERT INTO utilisateur (login, email, password, role, nom, est_actif)
    VALUES 
    (%s, %s, %s, 'ROLE_admin', 'Admin', 1),
    (%s, %s, %s, 'ROLE_client', 'Client', 1),
    (%s, %s, %s, 'ROLE_client', 'Client2', 1)
    '''
    mycursor.execute(sql, ('admin', 'admin@admin.fr', admin_password,
                           'client', 'client@client.fr', client_password,
                           'client2', 'client2@client2.fr', client2_password))

    sql = ''' 
    CREATE TABLE type_meuble(
        id_type_meuble INT AUTO_INCREMENT PRIMARY KEY,
        libelle_type_meuble VARCHAR(255) NOT NULL
    ) DEFAULT CHARSET utf8;  
    '''
    mycursor.execute(sql)
    sql = ''' 
    INSERT INTO type_meuble (libelle_type_meuble)
    VALUES 
    ('TABLE'), ('CHAISE'), ('CANAPE'), ('FAUTEUIL'), ('BANQUETTE'), ('BUREAU'),('CONSOLE'), ('TABOURET')
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE etat (
        id_etat INT AUTO_INCREMENT PRIMARY KEY,
        libelle VARCHAR(255) NOT NULL
    ) DEFAULT CHARSET=utf8;  
    '''
    mycursor.execute(sql)
    sql = ''' 
    INSERT INTO etat (libelle)
    VALUES 
    ('En cours de traitement'),
    ('Expédié'),
    ('Livré')
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE declinaison (
        id_declinaison INT AUTO_INCREMENT PRIMARY KEY,
        libelle VARCHAR(50) NOT NULL
    );
    '''
    mycursor.execute(sql)

    sql = '''
    INSERT INTO declinaison (libelle) VALUES
    ('Rose'), ('Noir'), ('Gris'), ('Brun');
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE meuble (
        id_meuble INT AUTO_INCREMENT PRIMARY KEY,
        nom_meuble VARCHAR(255) NOT NULL,
        prix_meuble DECIMAL(10,2) NOT NULL,
        stock INT NOT NULL,
        description TEXT,
        photo_url VARCHAR(255),
        type_meuble INT,
        FOREIGN KEY (type_meuble) REFERENCES type_meuble(id_type_meuble)
    ) DEFAULT CHARSET=utf8;  
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE adresse (
        id_adresse INT AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(255) NOT NULL,
        rue VARCHAR(255) NOT NULL,
        code_postal VARCHAR(10) NOT NULL,
        ville VARCHAR(255) NOT NULL,
        utilisateur_id INT,
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur)
    );
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE commande (
        id_commande INT AUTO_INCREMENT PRIMARY KEY,
        date_achat DATE NOT NULL,
        utilisateur_id INT,
        etat_id INT,
        adresse_livraison_id INT,
        adresse_facturation_id INT,
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (etat_id) REFERENCES etat(id_etat),
        FOREIGN KEY (adresse_livraison_id) REFERENCES adresse(id_adresse),
        FOREIGN KEY (adresse_facturation_id) REFERENCES adresse(id_adresse)
    ) DEFAULT CHARSET=utf8;  
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE ligne_commande(
        commande_id INT,
        meuble_id INT,
        prix DECIMAL(10,2) NOT NULL,
        quantite INT NOT NULL,
        PRIMARY KEY (commande_id, meuble_id),
        FOREIGN KEY (commande_id) REFERENCES commande(id_commande),
        FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble)
    );
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE ligne_panier (
        utilisateur_id INT,
        meuble_id INT,
        quantite INT NOT NULL,
        date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (utilisateur_id, meuble_id),
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble)
    );  
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE liste_envies (
        utilisateur_id INT,
        meuble_id INT,
        date_ajout DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (utilisateur_id, meuble_id),
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble)
    );
    '''
    mycursor.execute(sql)

    sql = '''
    CREATE TABLE historique (
        utilisateur_id INT,
        meuble_id INT,
        date_consultation DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (utilisateur_id, meuble_id),
        FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
        FOREIGN KEY (meuble_id) REFERENCES meuble(id_meuble)
    );
    '''
    mycursor.execute(sql)

    sql = ''' 
    CREATE TABLE commentaire(
       utilisateur_id INT,
       meuble_id INT,
       date_publication DATETIME,
       commentaire VARCHAR(255),
       valider INT,
       PRIMARY KEY(utilisateur_id, meuble_id, date_publication),
       FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
       FOREIGN KEY(meuble_id) REFERENCES meuble(id_meuble)
    ) DEFAULT CHARSET=utf8;
    '''
    mycursor.execute(sql)

    sql = ''' 
    INSERT INTO meuble (nom_meuble, description, prix_meuble, stock, photo_url, type_meuble)
    VALUES 
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s),
    (%s, %s, %s, %s, %s, %s)
    '''
    meuble_data = [
        ('Banquette', 'Banquette en bois de sapin coupé à la mains', 1200.00, 100 ,'banquette_bois.jpg', 5),
        ('Bureau', 'Bureau en bois de forêt', 40.99, 50 , 'bureau_en_bois.jpg', 6),
        ('Bureau_Plast', 'Bureau en plastique de luxe fait maison', 3045.89, 200 , 'bureau_en_plastoc.webp',6),
        ('Canape', 'Canape en tissus résistant à tout', 50.45, 150, 'canap_en_tissus.webp',3),
        ('Canape_Plast', 'Canape en plastique super comfortable', 289.67, 30 ,'canape_en plastique.png', 3),
        ('Chaise', 'Chaise en métal très design', 578.90, 250, 'chaise_en_metal.jpg', 2),
        ('Chaise_Plast', 'Chaise en plastique parfait pour le camping', 9999.99, 100, 'chaise_en_plastoc.jpg', 2),
        ('Chaise_Pli', 'Chaise pliante en bois très stylax', 2.00, 155,'chaise_pliante_bois.jpg', 2),
        ('Console', 'Console en metal pour décorer tout type de pièce', 343.54, 300,'console_metal.webp', 7),
        ('Fauteuil_Meta', 'Fauteuil en cuir et metal design et comfortable', 567.43, 25,'fauteuil_cuir_metal.webp', 4),
        ('Fauteuil_Meta', 'Fauteuil full metal soudé à la main', 20.00, 35,'fauteuil_en_metal.jpg', 4),
        ('Table_Bass', 'Table basse en bois foncé', 7.00, 100, 'table_basse_en_bois.jpg',1),
        ('Table', 'Table en bois massif magnifique', 4546.65, 230, 'table_en_bois_massif.jpg',1),
        ('Table_Meta', 'Table en métal ideal pour diner a Versaille', 56.78, 55,'table_en_metal.jpg', 1),
        ('Tabouret', 'Tabouret pour étudiant', 1.00, 29, 'tabouret_en_bois.jpg', 8)
    ]
    mycursor.execute(sql, [item for sublist in meuble_data for item in sublist])

    sql = '''
    INSERT INTO commentaire (utilisateur_id, meuble_id, date_publication, commentaire, valider) VALUES
        (2, 1, '2024-01-01 10:00:00', 'Excellente capacité de stockage, je recommande !', 1),
        (3, 2, '2024-01-02 11:30:00', 'Transfert rapide, design élégant', 1),
        (2, 3, '2024-01-03 14:15:00', 'Bon rapport qualité-prix, mais un peu fragile', 0);
    '''
    mycursor.execute(sql)

    get_db().commit()
    return redirect('/')
