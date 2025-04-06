#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db
from controllers.client_panier import calculer_prix_total_panier

client_meuble = Blueprint('client_meuble', __name__,
                          template_folder='templates')


@client_meuble.route('/client/index')
@client_meuble.route('/client/meuble/show')  # remplace /client
def client_meuble_show():  # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Récupération des articles du panier avec leurs déclinaisons
    sql = '''
        SELECT lp.*, m.nom_meuble, dm.prix_declinaison, mat.libelle_materiau,
               (SELECT COUNT(*) FROM declinaison_meuble dm2 WHERE dm2.meuble_id = m.id_meuble) as nb_declinaisons
        FROM ligne_panier lp
        JOIN declinaison_meuble dm ON lp.declinaison_meuble_id = dm.id_declinaison_meuble
        JOIN meuble m ON dm.meuble_id = m.id_meuble
        JOIN materiau mat ON dm.materiau_id = mat.id_materiau
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    # Calcul du prix total du panier
    prix_total_panier = calculer_prix_total_panier()

    # Récupération des meubles
    sql = '''
        SELECT m.*, dm.*, 
        (SELECT COUNT(*) FROM declinaison_meuble dm2 WHERE dm2.meuble_id = m.id_meuble) as nb_declinaisons,
        (SELECT SUM(stock) FROM declinaison_meuble dm2 WHERE dm2.meuble_id = m.id_meuble) as stock_total
        FROM meuble m
        JOIN declinaison_meuble dm ON m.id_meuble = dm.meuble_id
        WHERE m.disponible = 1
    '''
    mycursor.execute(sql)
    meubles = mycursor.fetchall()

    # pour le filtre
    sql = '''SELECT * FROM type_meuble'''
    mycursor.execute(sql)
    types_meuble = mycursor.fetchall()

    return render_template('client/boutique/panier_meuble.html',
                         meubles=meubles,
                         articles_panier=articles_panier,
                         prix_total_panier=prix_total_panier,
                         types_meuble=types_meuble)

@client_meuble.route('/client/meuble/declinaisons')
def client_meuble_declinaisons():
    id_meuble = request.args.get('id_meuble')
    if not id_meuble:
        flash('Aucun meuble sélectionné', 'error')
        return redirect('/client/meuble/show')
        
    mycursor = get_db().cursor()

    # Récupérer les informations du meuble
    sql = '''
    SELECT m.*, tm.libelle_type_meuble
    FROM meuble m
    JOIN type_meuble tm ON m.type_meuble_id = tm.id_type_meuble
    WHERE m.id_meuble = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    meuble = mycursor.fetchone()

    if not meuble:
        flash('Meuble non trouvé', 'error')
        return redirect('/client/meuble/show')

    # Récupérer toutes les déclinaisons du meuble
    sql = '''
    SELECT dm.*, mat.libelle_materiau
    FROM declinaison_meuble dm
    JOIN materiau mat ON dm.materiau_id = mat.id_materiau
    WHERE dm.meuble_id = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    declinaisons = mycursor.fetchall()

    if not declinaisons:
        flash('Aucune déclinaison disponible pour ce meuble', 'error')
        return redirect('/client/meuble/show')

    return render_template('client/boutique/choix_declinaison.html',
                         meuble=meuble,
                         declinaisons=declinaisons)
