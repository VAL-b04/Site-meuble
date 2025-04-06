#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_chiffre_affaire():
    mycursor = get_db().cursor()
    sql = '''
        SELECT COUNT(DISTINCT lc.commande_id) as nb_commandes,
        SUM(lc.quantite_lc) as nb_meuble,
        SUM(lc.quantite_lc * lc.prix_lc) AS total,
        LEFT(a.code_postal,2) as dep,
        SUM(lc.quantite_lc * lc.prix_lc) / SUM(lc.quantite_lc) as prix_moyen_meuble,
        SUM(lc.quantite_lc) / COUNT(DISTINCT lc.commande_id) as nb_meuble_moyen,
        SUM(lc.quantite_lc * lc.prix_lc) / COUNT(DISTINCT lc.commande_id) as panier_moyen
        FROM ligne_commande lc
        JOIN commande c ON lc.commande_id = c.id_commande
        JOIN adresse a ON c.adresse_id_fact = a.id_adresse
        JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
        GROUP BY dep
        ;
        '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()
    labels = [str(row['dep']) for row in datas_show]
    values = [int(row['panier_moyen']) for row in datas_show]
    values2 = [int(row['total']) for row in datas_show]

    sql = '''
    SELECT lc.commande_id,
    SUM(lc.quantite_lc) as nb_meuble,
    SUM(lc.quantite_lc * lc.prix_lc) AS total
    FROM ligne_commande lc
    JOIN commande c ON lc.commande_id = c.id_commande
    GROUP BY lc.commande_id
    ;
    '''
    mycursor.execute(sql)
    datas_show2 = mycursor.fetchall()
    labels2 = [str(row['commande_id']) for row in datas_show2]

    values3 = ""
    for row in datas_show2:
        if values3 == "":
            values3 = ("{x: "+str(row['total']+1)+", y: "+str(row['nb_meuble'])+"},")
        else:
            values3 = values3 + ("{x: "+str(row['total']+1)+", y: "+str(row['nb_meuble'])+"},")
    values3 = values3[:-1]
    values3 = "["+values3+"]"

    print("datas_show = " + str(datas_show))
    print("labels = " + str(labels))
    print("values = " + str(values))
    print("values2 = " + str(values2))
    print("datas_show2 = " + str(datas_show2))
    print("labels2 = " + str(labels2))
    print("values3 = " + str(values3))


    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , datas_show=datas_show
                           , labels=labels
                           , values=values
                           , values2=values2
                           , datas_show2=datas_show2
                           , labels2=labels2
                           , values3=values3)


# sujet 3 : adresses


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()

    sql = '''
    SELECT 
        LEFT(a.code_postal,2) as dep,
        COUNT(DISTINCT lc.commande_id) as nb_commandes,
        SUM(lc.quantite_lc * lc.prix_lc) as chiffre_affaire
    FROM ligne_commande lc
    JOIN commande c ON lc.commande_id = c.id_commande
    JOIN adresse a ON c.adresse_id_fact = a.id_adresse
    GROUP BY dep
    ORDER BY dep
    '''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()

    # recherche de la valeur maxi pour les indices
    maxCommandes = 0
    maxCA = 0

    for element in adresses:
        if element['nb_commandes'] > maxCommandes:
            maxCommandes = element['nb_commandes']
        if element['chiffre_affaire'] > maxCA:
            maxCA = element['chiffre_affaire']

    # calcul des indices pour chaque département
    for element in adresses:
        element['indice_commandes'] = round(element['nb_commandes'] / maxCommandes, 2) if maxCommandes > 0 else 0
        element['indice_ca'] = round(element['chiffre_affaire'] / maxCA, 2) if maxCA > 0 else 0

    return render_template('admin/dataviz/dataviz_etat_map.html', adresses=adresses)


@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_meuble_stock():
    mycursor = get_db().cursor()
    sql = '''
        SELECT 
            tm.libelle_type_meuble,
            COUNT(DISTINCT n.utilisateur_id) as nb_notes,
            COALESCE(AVG(n.note), 0) as moyenne_notes,
            COUNT(c.commentaire) as nb_commentaires,
            COUNT(CASE WHEN c.valider = 1 THEN 1 END) as nb_commentaires_valides
        FROM type_meuble tm
        LEFT JOIN meuble m ON tm.id_type_meuble = m.type_meuble_id
        LEFT JOIN note n ON m.id_meuble = n.meuble_id
        LEFT JOIN commentaire c ON m.id_meuble = c.meuble_id
        GROUP BY tm.id_type_meuble, tm.libelle_type_meuble
        ORDER BY tm.libelle_type_meuble
    '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()

    # Préparation des données pour les graphiques
    labels = [row['libelle_type_meuble'] for row in datas_show]
    values = [float(row['moyenne_notes']) for row in datas_show]
    values2 = [int(row['nb_commentaires']) for row in datas_show]
    values3 = [int(row['nb_notes']) for row in datas_show]

    return render_template('admin/dataviz/dataviz_etat_1.html',
                           datas_show=datas_show,
                           labels=labels,
                           values=values,
                           values2=values2,
                           values3=values3)


@admin_dataviz.route('/admin/dataviz/commentaires')
def show_dataviz_commentaires():
    # Récupération des catégories
    cursor = get_db().cursor()
    cursor.execute("SELECT id_type_meuble, libelle_type_meuble FROM type_meuble ORDER BY libelle_type_meuble")
    categories = cursor.fetchall()

    # Récupération des statistiques globales
    cursor.execute("""
        SELECT 
            tm.libelle_type_meuble,
            COUNT(DISTINCT n.utilisateur_id) as nb_notes,
            COALESCE(AVG(n.note), 0) as moyenne_notes,
            COUNT(c.commentaire) as nb_commentaires,
            COUNT(CASE WHEN c.valider = 1 THEN 1 END) as nb_commentaires_valides
        FROM type_meuble tm
        LEFT JOIN meuble m ON tm.id_type_meuble = m.type_meuble_id
        LEFT JOIN note n ON m.id_meuble = n.meuble_id
        LEFT JOIN commentaire c ON m.id_meuble = c.meuble_id
        GROUP BY tm.id_type_meuble, tm.libelle_type_meuble
        ORDER BY tm.libelle_type_meuble
    """)
    datas_show = cursor.fetchall()

    # Préparation des données pour les graphiques
    labels = []
    values = []
    values2 = []
    values3 = []

    for row in datas_show:
        labels.append(row['libelle_type_meuble'])
        values.append(float(row['moyenne_notes']))
        values2.append(row['nb_commentaires'])
        values3.append(row['nb_notes'])

    return render_template('admin/dataviz/dataviz_commentaires.html',
                           datas_show=datas_show,
                           labels=labels,
                           values=values,
                           values2=values2,
                           values3=values3,
                           categories=categories)


@admin_dataviz.route('/admin/dataviz/commentaires/articles/<int:id_type_meuble>')
def get_articles_stats(id_type_meuble):
    cursor = get_db().cursor()

    # Récupération des statistiques par article
    cursor.execute("""
        SELECT 
            m.id_meuble,
            m.nom_meuble,
            COUNT(DISTINCT n.utilisateur_id) as nb_notes,
            COALESCE(AVG(n.note), 0) as moyenne_notes,
            COUNT(c.commentaire) as nb_commentaires,
            COUNT(CASE WHEN c.valider = 1 THEN 1 END) as nb_commentaires_valides
        FROM meuble m
        LEFT JOIN note n ON m.id_meuble = n.meuble_id
        LEFT JOIN commentaire c ON m.id_meuble = c.meuble_id
        WHERE m.type_meuble_id = %s
        GROUP BY m.id_meuble, m.nom_meuble
        ORDER BY m.nom_meuble
    """, (id_type_meuble,))
    articles = cursor.fetchall()

    # Préparation des données pour les graphiques
    labels = []
    values_notes = []
    values_comments = []
    values_nb_notes = []

    for article in articles:
        labels.append(article['nom_meuble'])
        values_notes.append(float(article['moyenne_notes']))
        values_comments.append(article['nb_commentaires'])
        values_nb_notes.append(article['nb_notes'])

    return jsonify({
        'articles': articles,
        'labels': labels,
        'values_notes': values_notes,
        'values_comments': values_comments,
        'values_nb_notes': values_nb_notes
    })


@admin_dataviz.route('/admin/dataviz/stocks')
def show_stocks():
    mycursor = get_db().cursor()
    
    # Requête pour obtenir les données de stock par déclinaison
    sql = '''
        SELECT 
            m.nom_meuble,
            mat.libelle_materiau,
            dm.stock,
            dm.prix_declinaison,
            (dm.stock * dm.prix_declinaison) as cout_stock
        FROM declinaison_meuble dm
        JOIN meuble m ON dm.meuble_id = m.id_meuble
        JOIN materiau mat ON dm.materiau_id = mat.id_materiau
        ORDER BY m.nom_meuble, mat.libelle_materiau
    '''
    mycursor.execute(sql)
    stocks_data = mycursor.fetchall()
    
    # Préparation des données pour les graphiques
    labels = [row['nom_meuble'] + ' - ' + row['libelle_materiau'] for row in stocks_data]
    stock_values = [row['stock'] for row in stocks_data]
    cout_values = [float(row['cout_stock']) for row in stocks_data]
    
    return render_template('admin/dataviz/dataviz_stocks.html',
                         stocks_data=stocks_data,
                         labels=labels,
                         stock_values=stock_values,
                         cout_values=cout_values)





