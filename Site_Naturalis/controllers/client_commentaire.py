#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

from controllers.client_liste_envies import client_historique_add

client_commentaire = Blueprint('client_commentaire', __name__,
                               template_folder='templates')


@client_commentaire.route('/client/meuble/details', methods=['GET'])
def client_meuble_details():
    mycursor = get_db().cursor()
    id_meuble = request.args.get('id_meuble', None)
    id_client = session['id_user']

    print("ID meuble reçu:", id_meuble)
    print("ID client:", id_client)

    ## partie 4
    # client_historique_add(id_meuble, id_client)

    sql = '''
    SELECT m.*, 
           tm.libelle_type_meuble,
           m.description_meuble as description,
           COALESCE(AVG(n.note), 0) as moyenne_notes,
           COUNT(DISTINCT n.utilisateur_id) as nb_notes,
           COALESCE(SUM(dm.stock), 0) as stock_total
    FROM meuble m
    LEFT JOIN type_meuble tm ON m.type_meuble_id = tm.id_type_meuble
    LEFT JOIN note n ON m.id_meuble = n.meuble_id
    LEFT JOIN declinaison_meuble dm ON m.id_meuble = dm.meuble_id
    WHERE m.id_meuble = %s
    GROUP BY m.id_meuble, m.nom_meuble, m.disponible, m.prix_meuble, 
             m.description_meuble, m.image_meuble, m.type_meuble_id,
             tm.libelle_type_meuble
    '''
    print("SQL query:", sql)
    print("Paramètres:", (id_meuble,))

    mycursor.execute(sql, (id_meuble,))
    meuble = mycursor.fetchone()
    print("Résultat de la requête:", meuble)

    if meuble is None:
        print("Aucun meuble trouvé avec l'ID:", id_meuble)
        abort(404, "pb id meuble")

    # Récupérer les déclinaisons du meuble
    sql = '''
    SELECT dm.*, m.libelle_materiau
    FROM declinaison_meuble dm
    JOIN materiau m ON dm.materiau_id = m.id_materiau
    WHERE dm.meuble_id = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    declinaisons = mycursor.fetchall()

    # Récupérer le nombre de commandes pour ce meuble par ce client
    sql = '''
    SELECT COUNT(*) as nb_commandes_meuble
    FROM ligne_commande lc
    JOIN commande c ON lc.commande_id = c.id_commande
    JOIN declinaison_meuble dm ON lc.declinaison_meuble_id = dm.id_declinaison_meuble
    WHERE c.utilisateur_id = %s AND dm.meuble_id = %s
    '''
    mycursor.execute(sql, (id_client, id_meuble))
    commandes_meubles = mycursor.fetchone()

    # Récupérer la note de l'utilisateur pour ce meuble
    sql = '''
    SELECT note
    FROM note
    WHERE utilisateur_id = %s AND meuble_id = %s
    '''
    mycursor.execute(sql, (id_client, id_meuble))
    note = mycursor.fetchone()
    if note:
        note = note['note']

    # Récupérer le nombre de commentaires
    sql = '''
    SELECT COUNT(*) as nb_commentaires_total,
           COUNT(CASE WHEN utilisateur_id = %s THEN 1 END) as nb_commentaires_utilisateur,
           COUNT(CASE WHEN valider = 1 THEN 1 END) as nb_commentaires_valides_total,
           COUNT(CASE WHEN utilisateur_id = %s AND valider = 1 THEN 1 END) as nb_commentaires_valides_utilisateur
    FROM commentaire
    WHERE meuble_id = %s
    '''
    mycursor.execute(sql, (id_client, id_client, id_meuble))
    nb_commentaires = mycursor.fetchone()

    # Récupérer les commentaires
    sql = '''
    SELECT c.*, u.nom_utilisateur
    FROM commentaire c
    JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
    WHERE c.meuble_id = %s
    ORDER BY c.date_publication DESC
    '''
    mycursor.execute(sql, (id_meuble,))
    commentaires = mycursor.fetchall()

    return render_template('client/meuble_info/meuble_details.html'
                           , meuble=meuble
                           , declinaisons=declinaisons
                           , commandes_meubles=commandes_meubles
                           , note=note
                           , nb_commentaires=nb_commentaires
                           , commentaires=commentaires
                           )


@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    commentaire = request.form.get('commentaire', None)
    id_client = session['id_user']
    id_meuble = request.form.get('id_meuble', None)
    if commentaire == '':
        flash(u'Commentaire non prise en compte')
        return redirect('/client/meuble/details?id_meuble=' + id_meuble)
    if commentaire != None and len(commentaire) < 3:
        flash(u'Commentaire avec plus de 2 caractères', 'alert-warning')
        return redirect('/client/meuble/details?id_meuble=' + id_meuble)

    tuple_insert = (commentaire, id_client, id_meuble)
    print(tuple_insert)
    sql = '''INSERT INTO commentaire (commentaire, utilisateur_id, meuble_id, date_publication, valider) 
             VALUES (%s, %s, %s, NOW(), 0)'''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect('/client/meuble/details?id_meuble=' + id_meuble)


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_detete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_meuble = request.form.get('id_meuble', None)
    date_publication = request.form.get('date_publication', None)
    sql = '''DELETE FROM commentaire 
             WHERE utilisateur_id = %s 
             AND meuble_id = %s 
             AND date_publication = %s'''
    tuple_delete = (id_client, id_meuble, date_publication)
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/meuble/details?id_meuble=' + id_meuble)


@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_meuble = request.form.get('id_meuble', None)
    tuple_insert = (note, id_client, id_meuble)
    print(tuple_insert)
    sql = '''INSERT INTO note (note, utilisateur_id, meuble_id) VALUES (%s, %s, %s)'''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    return redirect('/client/meuble/details?id_meuble=' + id_meuble)


@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_meuble = request.form.get('id_meuble', None)
    tuple_update = (note, id_client, id_meuble)
    print(tuple_update)
    sql = '''UPDATE note SET note = %s WHERE utilisateur_id = %s AND meuble_id = %s'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    return redirect('/client/meuble/details?id_meuble=' + id_meuble)


@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_meuble = request.form.get('id_meuble', None)
    tuple_delete = (id_client, id_meuble)
    print(tuple_delete)
    sql = '''DELETE FROM note WHERE utilisateur_id = %s AND meuble_id = %s'''
    mycursor.execute(sql, tuple_delete)
    get_db().commit()
    return redirect('/client/meuble/details?id_meuble=' + id_meuble)