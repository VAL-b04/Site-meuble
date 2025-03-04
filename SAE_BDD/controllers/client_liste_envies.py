#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                                template_folder='templates')

# Pas Touche LIV 3
@client_liste_envies.route('/client/envie/add', methods=['get'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''
    INSERT INTO liste_envies (utilisateur_id, meuble_id)
    VALUES (%s, %s)
    '''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()
    return redirect('/client/article/show')


@client_liste_envies.route('/client/envie/delete', methods=['get'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''
    DELETE FROM liste_envies
    WHERE utilisateur_id = %s AND meuble_id = %s
    '''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()
    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''
    SELECT c.*,
           (SELECT COUNT(*) FROM meuble WHERE id_meuble = c.id_meuble) AS nb_declinaisons,
           (SELECT COUNT(*) FROM liste_envies WHERE meuble_id = c.id_meuble AND utilisateur_id != %s) AS nb_wish_list_other
    FROM meuble c
    JOIN liste_envies le ON c.id_meuble = le.meuble_id
    WHERE le.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client, id_client))
    articles_liste_envies = mycursor.fetchall()

    sql = '''
    SELECT c.*, h.date_consultation
    FROM meuble c
    JOIN historique h ON c.id_meuble = h.meuble_id
    WHERE h.utilisateur_id = %s
    ORDER BY h.date_consultation DESC
    LIMIT 6
    '''
    mycursor.execute(sql, (id_client,))
    articles_historique = mycursor.fetchall()

    nb_liste_envies = len(articles_liste_envies)
    nb_liste_historique = len(articles_historique)

    info_wishlist = {}
    info_wishlist_categorie = {}
    if articles_liste_envies:
        premier_article = articles_liste_envies[0]
        info_wishlist = {
            'nom': premier_article['nom'] if 'nom' in premier_article else '',
            'nb_wish_list_other': premier_article['nb_wish_list_other']
        }

        sql = '''
        SELECT t.libelle,
               (SELECT COUNT(*) FROM liste_envies le
                JOIN meuble c ON le.meuble_id = c.id_meuble
                WHERE c.type_meuble = %s AND le.utilisateur_id = %s) AS nb_wish_list_other_categorie
        FROM type_cle_usb t
        WHERE t.id_type_meuble = %s
        '''
        mycursor.execute(sql, (premier_article['type_meuble'], id_client, premier_article['type_meuble']))
        info_wishlist_categorie = mycursor.fetchone()

    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique,
                           nb_liste_envies=nb_liste_envies,
                           nb_liste_historique=nb_liste_historique,
                           info_wishlist=info_wishlist,
                           info_wishlist_categorie=info_wishlist_categorie)


def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()
    client_id = session['id_user']
    sql = '''
    SELECT *
    FROM historique
    WHERE utilisateur_id = %s AND meuble_id = %s
    '''
    mycursor.execute(sql, (client_id, article_id))
    historique_produit = mycursor.fetchone()
    if historique_produit:
        sql = '''
        UPDATE historique
        SET date_consultation = NOW()
        WHERE utilisateur_id = %s AND meuble_id = %s
        '''
        mycursor.execute(sql, (client_id, article_id))
    else:
        # si non, ajouter l'article dans l'historique
        sql = '''
        INSERT INTO historique (utilisateur_id, meuble_id, date_consultation)
        VALUES (%s, %s, NOW())
        '''
        mycursor.execute(sql, (client_id, article_id))

    sql = '''
    DELETE FROM historique
    WHERE utilisateur_id = %s
    AND meuble_id NOT IN (
        SELECT meuble_id
        FROM (
            SELECT meuble_id
            FROM historique
            WHERE utilisateur_id = %s
            ORDER BY date_consultation DESC
            LIMIT 6
        ) AS sub
    )
    '''
    mycursor.execute(sql, (client_id, client_id))
    get_db().commit()