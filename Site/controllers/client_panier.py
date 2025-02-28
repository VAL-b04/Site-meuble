#! /usr/bin/python
# -*- coding:utf-8 -*-
import time

from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                          template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_meuble = request.form.get('id_declinaison_meuble')

    print("Debug - id_declinaison_meuble:", id_declinaison_meuble)  # Debug

    if not id_declinaison_meuble:
        flash(u'Erreur : produit non trouvé (ID manquant)', 'alert-warning')
        return redirect('/client/meuble/show')

    quantite = int(request.form.get('quantite', 1))

    # Vérifier le stock disponible
    sql = """
        SELECT stock, prix_declinaison 
        FROM declinaison_meuble
        WHERE id_declinaison_meuble = %s
    """
    mycursor.execute(sql, (id_declinaison_meuble,))
    result = mycursor.fetchone()

    print("Debug - Stock query result:", result)  # Debug

    if not result:
        flash(u'Erreur : produit non trouvé dans la base', 'alert-warning')
        return redirect('/client/meuble/show')

    stock_disponible = result['stock']
    prix = result['prix_declinaison']

    # Vérifier si la quantité demandée est valide
    if quantite < 1 or quantite > stock_disponible:
        flash(u'Quantité invalide ou stock insuffisant', 'alert-warning')
        return redirect('/client/meuble/show')

    try:
        # Début de la transaction
        get_db().begin()

        # Vérifier si l'article est déjà dans le panier
        sql = """
            SELECT quantite_lp 
            FROM ligne_panier
            WHERE utilisateur_id = %s AND declinaison_meuble_id = %s
        """
        mycursor.execute(sql, (id_client, id_declinaison_meuble))
        ligne_panier = mycursor.fetchone()

        if ligne_panier:
            # Mettre à jour la quantité si l'article existe déjà
            nouvelle_quantite = ligne_panier['quantite_lp'] + quantite
            if nouvelle_quantite > stock_disponible:
                flash(u'Stock insuffisant pour la quantité totale demandée', 'alert-warning')
                get_db().rollback()
                return redirect('/client/meuble/show')

            sql = """
                UPDATE ligne_panier 
                SET quantite_lp = %s
                WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
            """
            mycursor.execute(sql, (nouvelle_quantite, id_declinaison_meuble, id_client))
        else:
            # Ajouter une nouvelle ligne dans le panier
            sql = """
                INSERT INTO ligne_panier 
                (declinaison_meuble_id, utilisateur_id, quantite_lp, date_ajout) 
                VALUES (%s, %s, %s, CURRENT_DATE)
            """
            mycursor.execute(sql, (id_declinaison_meuble, id_client, quantite))

        # Mettre à jour le stock
        sql = """
            UPDATE declinaison_meuble 
            SET stock = stock - %s 
            WHERE id_declinaison_meuble = %s
        """
        mycursor.execute(sql, (quantite, id_declinaison_meuble))

        # Valider la transaction
        get_db().commit()
        flash(u'Article ajouté au panier', 'alert-success')

    except Exception as e:
        get_db().rollback()
        print("Debug - Error:", str(e))  # Debug
        flash(u'Erreur lors de l\'ajout au panier: ' + str(e), 'alert-danger')

    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_meuble = request.form.get('id_declinaison_meuble', '')

    # ---------
    # partie 2 : on supprime une déclinaison de meuble
    # id_declinaison_meuble = request.form.get('id_declinaison_meuble', None)

    sql = '''
    SELECT * FROM ligne_panier
    WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_declinaison_meuble, id_client))
    meuble_panier = mycursor.fetchone()

    quantite = meuble_panier['quantite_lp']

    if not (meuble_panier is None) and quantite > 1:
        sql = '''
        UPDATE ligne_panier SET quantite_lp = quantite_lp - 1
        WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
        '''

        quantite = 1
    else:
        sql = '''
        DELETE FROM ligne_panier
        WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
        '''

    mycursor.execute(sql, (id_declinaison_meuble, id_client))

    # mise à jour du stock de meuble disponible

    sql2 = '''UPDATE declinaison_meuble SET stock = stock + %s WHERE id_declinaison_meuble = %s '''
    mycursor.execute(sql2, (quantite, id_declinaison_meuble))

    get_db().commit()
    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']
    sql = '''SELECT * FROM ligne_panier WHERE utilisateur_id = %s'''
    mycursor.execute(sql, client_id)

    items_panier = mycursor.fetchall()
    for item in items_panier:
        meuble_id = item['declinaison_meuble_id']

        sql = '''DELETE FROM ligne_panier WHERE utilisateur_id = %s AND declinaison_meuble_id = %s'''
        mycursor.execute(sql, (client_id, meuble_id))

        sql2 = '''UPDATE declinaison_meuble SET stock = stock + %s WHERE id_declinaison_meuble = %s'''
        mycursor.execute(sql2, (item['quantite_lp'], meuble_id))

    get_db().commit()
    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_meuble = request.form.get('id_declinaison_meuble', '')
    data = (id_declinaison_meuble, id_client)

    # id_declinaison_meuble = request.form.get('id_declinaison_meuble')

    sql = '''
        SELECT quantite_lp FROM ligne_panier
        WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
    '''

    mycursor.execute(sql, data)
    quantite = mycursor.fetchone()['quantite_lp']

    sql = '''
        DELETE FROM ligne_panier
        WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
    '''

    mycursor.execute(sql, (id_declinaison_meuble, id_client))

    sql2 = '''UPDATE declinaison_meuble SET stock = stock + %s WHERE id_declinaison_meuble = %s '''
    mycursor.execute(sql2, (quantite, id_declinaison_meuble))

    get_db().commit()
    return redirect('/client/meuble/show')