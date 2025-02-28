#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint, request, render_template, redirect, flash, session
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                            template_folder='templates')

@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
        SELECT * FROM ligne_panier
        WHERE utilisateur_id = %s;
    '''
    mycursor.execute(sql, (id_client,))
    meubles_panier = mycursor.fetchall()

    prix_total = None
    if meubles_panier:
        sql = '''
            SELECT SUM(prix_declinaison * quantite_lp) AS prix_total
            FROM ligne_panier
            JOIN declinaison_meuble ON ligne_panier.declinaison_meuble_id = declinaison_meuble.id_declinaison_meuble
            WHERE utilisateur_id = %s;
        '''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()

    sql = '''
        SELECT * 
        FROM adresse
        JOIN concerne ON adresse.id_adresse = concerne.adresse_id
        WHERE utilisateur_id = %s AND adresse.valide = 1;
    '''
    mycursor.execute(sql, (id_client,))
    adresses = mycursor.fetchall()

    sql = '''
    SELECT adresse_id_livr, adresse_id_fact
    FROM commande 
    WHERE id_commande = (SELECT MAX(id_commande) FROM commande WHERE utilisateur_id = %s)
    '''
    mycursor.execute(sql, (id_client,))
    id_adresse_fav = mycursor.fetchone()

    return render_template('client/boutique/panier_validation_adresses.html',
                           adresses=adresses,
                           meubles_panier=meubles_panier,
                           prix_total=prix_total,
                           validation=1,
                           id_adresse_fav=id_adresse_fav)

@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    adresse_id_livr = request.form['id_adresse_livraison']
    adresse_id_fact = request.form.get('id_adresse_facturation', adresse_id_livr)

    if adresse_id_fact == adresse_id_livr:
        flash('Adresse de livraison et de facturation identiques, veuillez utilisez la checkbox', 'alert-warning')
        return redirect('/client/article/show')

    sql = "SELECT * FROM ligne_panier WHERE utilisateur_id=%s"
    mycursor.execute(sql, (id_client,))
    items_ligne_panier = mycursor.fetchall()
    if not items_ligne_panier:
        flash('Pas d\'articles dans le panier')
        return redirect('/client/article/show')

    sql = "INSERT INTO commande(date_achat, utilisateur_id, etat_id, adresse_id_fact, adresse_id_livr) VALUES (CURRENT_TIMESTAMP, %s, 1, %s, %s)"
    mycursor.execute(sql, (id_client, adresse_id_fact, adresse_id_livr))
    commande_id = mycursor.lastrowid

    for item in items_ligne_panier:
        sql = "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND declinaison_meuble_id = %s"
        mycursor.execute(sql, (id_client, item['declinaison_meuble_id']))

        sql = "INSERT INTO ligne_commande (commande_id, declinaison_meuble_id, prix_lc, quantite_lc) VALUES (%s, %s, %s, %s)"
        mycursor.execute(sql, (commande_id, item['declinaison_meuble_id'], item['prix_declinaison'], item['quantite_lp']))

    get_db().commit()
    flash('Commande ajoutÃ©e', 'alert-success')
    return redirect('/client/article/show')