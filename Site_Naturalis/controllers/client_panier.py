#! /usr/bin/python
# -*- coding:utf-8 -*-
import time

from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                          template_folder='templates')


def calculer_prix_total_panier():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    
    sql = '''
        SELECT SUM(lp.quantite_lp * dm.prix_declinaison) as prix_total
        FROM ligne_panier lp
        JOIN declinaison_meuble dm ON lp.declinaison_meuble_id = dm.id_declinaison_meuble
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    result = mycursor.fetchone()
    return result['prix_total'] if result['prix_total'] is not None else 0


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_meuble = request.form.get('id_declinaison_meuble')
    quantite = int(request.form.get('quantite'))

    # Vérification du stock disponible
    sql = """
        SELECT stock FROM declinaison_meuble
        WHERE id_declinaison_meuble = %s
    """
    mycursor.execute(sql, id_declinaison_meuble)
    stock_disponible = mycursor.fetchone()['stock']

    if quantite <= 0:
        flash('La quantité doit être supérieure à 0')
        return redirect('/client/meuble/show')

    if quantite > stock_disponible:
        flash('Stock insuffisant')
        return redirect('/client/meuble/show')

    # Vérification si l'article est déjà dans le panier
    sql = """
        SELECT * FROM ligne_panier
        WHERE utilisateur_id = %s AND declinaison_meuble_id = %s
    """
    mycursor.execute(sql, (id_client, id_declinaison_meuble))
    ligne_panier = mycursor.fetchone()

    if ligne_panier is not None:
        # Vérification que le stock total (panier + nouvelle quantité) ne dépasse pas le stock disponible
        if ligne_panier['quantite_lp'] + quantite > stock_disponible:
            flash('Stock insuffisant pour cette quantité')
            return redirect('/client/meuble/show')
            
        sql = """
            UPDATE ligne_panier SET quantite_lp = quantite_lp + %s
            WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
        """
        mycursor.execute(sql, (quantite, id_declinaison_meuble, id_client))
    else:
        sql = """
            INSERT INTO ligne_panier (declinaison_meuble_id, utilisateur_id, quantite_lp, date_ajout) 
            VALUES (%s, %s, %s, CURRENT_DATE)
        """
        mycursor.execute(sql, (id_declinaison_meuble, id_client, quantite))

    # Mise à jour du stock
    sql = """
        UPDATE declinaison_meuble SET stock = stock - %s 
        WHERE id_declinaison_meuble = %s
    """
    mycursor.execute(sql, (quantite, id_declinaison_meuble))

    get_db().commit()
    flash('Article ajouté au panier')
    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_meuble = request.form.get('id_declinaison_meuble', '')

    sql = '''
    SELECT * FROM ligne_panier
    WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_declinaison_meuble, id_client))
    meuble_panier = mycursor.fetchone()

    if meuble_panier is None:
        flash('Article non trouvé dans le panier')
        return redirect('/client/meuble/show')

    quantite = 1  # On supprime une unité à la fois

    if meuble_panier['quantite_lp'] > 1:
        sql = '''
        UPDATE ligne_panier SET quantite_lp = quantite_lp - 1
        WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
        '''
    else:
        sql = '''
        DELETE FROM ligne_panier
        WHERE declinaison_meuble_id = %s AND utilisateur_id = %s
        '''

    mycursor.execute(sql, (id_declinaison_meuble, id_client))

    # Réincrémentation du stock
    sql2 = '''
        UPDATE declinaison_meuble 
        SET stock = stock + %s 
        WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql2, (quantite, id_declinaison_meuble))

    get_db().commit()
    flash('Article retiré du panier')
    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']
    
    # Récupération de tous les articles du panier
    sql = '''
        SELECT * FROM ligne_panier 
        WHERE utilisateur_id = %s
    '''
    mycursor.execute(sql, client_id)
    items_panier = mycursor.fetchall()

    # Pour chaque article, réincrémenter le stock et supprimer du panier
    for item in items_panier:
        sql = '''
            UPDATE declinaison_meuble 
            SET stock = stock + %s 
            WHERE id_declinaison_meuble = %s
        '''
        mycursor.execute(sql, (item['quantite_lp'], item['declinaison_meuble_id']))

        sql = '''
            DELETE FROM ligne_panier 
            WHERE utilisateur_id = %s 
            AND declinaison_meuble_id = %s
        '''
        mycursor.execute(sql, (client_id, item['declinaison_meuble_id']))

    get_db().commit()
    flash('Panier vidé')
    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_meuble = request.form.get('id_declinaison_meuble', '')

    # Récupération de la quantité à supprimer
    sql = '''
        SELECT quantite_lp 
        FROM ligne_panier
        WHERE declinaison_meuble_id = %s 
        AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_declinaison_meuble, id_client))
    result = mycursor.fetchone()

    if result is None:
        flash('Article non trouvé dans le panier')
        return redirect('/client/meuble/show')

    quantite = result['quantite_lp']

    # Suppression de la ligne du panier
    sql = '''
        DELETE FROM ligne_panier
        WHERE declinaison_meuble_id = %s 
        AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_declinaison_meuble, id_client))

    # Réincrémentation du stock
    sql2 = '''
        UPDATE declinaison_meuble 
        SET stock = stock + %s 
        WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql2, (quantite, id_declinaison_meuble))

    get_db().commit()
    flash('Article retiré du panier')
    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types', None)
    # test des variables puis
    # mise en session des variables

    if filter_word or filter_word == '':
        if len(filter_word) > 1:
            if filter_word.isalpha():
                session['filter_word'] = filter_word
            else:
                flash('Le mot doit être composé de lettres uniquement')
        else:
            if len(filter_word) == 1:
                flash('Le mot doit contenir au moins 2 lettres')
            else:
                session.pop('filter_word', None)

    if filter_prix_min or filter_prix_max:
        if filter_prix_min.isdecimal() and filter_prix_max.isdecimal():
            if int(filter_prix_min) < int(filter_prix_max):
                session['filter_prix_min'] = filter_prix_min
                session['filter_prix_max'] = filter_prix_max
            else:
                flash('Le prix minimum doit être inférieur au prix maximum')
        else:
            flash('Les prix doivent être des nombres entiers')
    if filter_types and filter_types != []:
        session['filter_types'] = filter_types

    print(session)
    return redirect('/client/meuble/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    # suppression  des variables en session
    session.pop('filter_word', None)
    session.pop('filter_types', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    print("suppr filtre")
    return redirect('/client/meuble/show')
