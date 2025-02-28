#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get', 'post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']

    id_commande = request.args.get('id_commande', None)

    sql = '''
    SELECT 
        commande.id_commande, 
        utilisateur.login, 
        commande.date_achat, 
        SUM(ligne_commande.quantite_lc) AS nbr_articles, 
        SUM(ligne_commande.prix_lc * ligne_commande.quantite_lc) AS prix_total,
        etat.libelle_etat AS libelle,
        commande.etat_id
    FROM commande
    JOIN utilisateur ON commande.utilisateur_id = utilisateur.id_utilisateur
    JOIN etat ON commande.etat_id = etat.id_etat
    JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
    GROUP BY commande.id_commande, utilisateur.login, commande.date_achat, etat.libelle_etat, commande.etat_id
    '''
    mycursor.execute(sql)
    commandes = mycursor.fetchall()

    if id_commande is not None:

        sql_articles = '''
        SELECT 
            meuble.nom_meuble AS nom, 
            ligne_commande.quantite_lc AS quantite, 
            (ligne_commande.prix_lc * ligne_commande.quantite_lc) AS prix_ligne, 
            ligne_commande.prix_lc AS prix,
            COUNT(DISTINCT declinaison_meuble.id_declinaison_meuble) AS nb_declinaisons
        FROM meuble 
        JOIN ligne_commande ON meuble.id_meuble = ligne_commande.declinaison_meuble_id
        LEFT JOIN declinaison_meuble ON meuble.id_meuble = declinaison_meuble.meuble_id
        WHERE ligne_commande.commande_id = %s
        GROUP BY meuble.id_meuble, ligne_commande.quantite_lc, ligne_commande.prix_lc
        '''
        mycursor.execute(sql_articles, (id_commande,))
        articles_commande = mycursor.fetchall()

        sql_commande_details = '''
        SELECT 
            u.login,
            c.date_achat,
            SUM(lc.quantite_lc) AS nbr_articles,
            SUM(lc.quantite_lc * lc.prix_lc) AS prix_total,
            e.libelle_etat AS libelle,
            al.nom_adresse AS nom_livraison,
            al.rue AS rue_livraison,
            al.code_postal AS code_postal_livraison,
            al.ville AS ville_livraison,
            af.nom_adresse AS nom_facturation,
            af.rue AS rue_facturation,
            af.code_postal AS code_postal_facturation,
            af.ville AS ville_facturation
        FROM commande c
        INNER JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
        INNER JOIN etat e ON c.etat_id = e.id_etat
        LEFT JOIN ligne_commande lc ON c.id_commande = lc.commande_id
        LEFT JOIN adresse al ON c.adresse_id_livr = al.id_adresse
        LEFT JOIN adresse af ON c.adresse_id_fact = af.id_adresse
        WHERE c.id_commande = %s
        GROUP BY c.id_commande, u.login, c.date_achat, e.libelle_etat, 
                 al.nom_adresse, al.rue, al.code_postal, al.ville, 
                 af.nom_adresse, af.rue, af.code_postal, af.ville
        '''
        mycursor.execute(sql_commande_details, (id_commande,))
        commande_adresses = mycursor.fetchone()

    return render_template('admin/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=commande_adresses)





@admin_commande.route('/admin/commande/valider', methods=['get', 'post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id is not None:
        print(commande_id)
        sql = '''UPDATE commande SET etat_id = 3 WHERE id_commande = %s'''
        mycursor.execute(sql, (commande_id,))
        get_db().commit()
    return redirect('/admin/commande/show')
