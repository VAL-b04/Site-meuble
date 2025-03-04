#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_article = Blueprint('admin_declinaison_article', __name__,
                                      template_folder='templates')


@admin_declinaison_article.route('/admin/declinaison_article/add')
def add_declinaison_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''
    SELECT id_meuble, nom_meuble, description, prix_meuble
    FROM meuble
    WHERE id_meuble = %s
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    sql = '''
    SELECT DISTINCT couleur
    FROM meuble
    '''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()

    sql = '''
    SELECT id_materiau, libelle_materiau
    FROM materiau
    '''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()

    d_taille_uniq = None
    d_couleur_uniq = None
    return render_template('admin/article/add_declinaison_article.html'
                           , article=article
                           , couleurs=couleurs
                           , tailles=tailles
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['POST'])
def valid_add_declinaison_article():
    mycursor = get_db().cursor()

    id_article = request.form.get('id_article')
    stock = request.form.get('stock')
    taille = request.form.get('taille')
    couleur = request.form.get('couleur')

    sql = '''
    INSERT INTO declinaison_article (meuble_id, stock, materiau_id, couleur)
    VALUES (%s, %s, %s, %s)
    '''
    mycursor.execute(sql, (id_article, stock, taille, couleur))
    get_db().commit()
    return redirect('/admin/article/edit?id_article=' + id_article)


@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['GET'])
def edit_declinaison_article():
    id_declinaison_article = request.args.get('id_declinaison_article')
    mycursor = get_db().cursor()
    sql = '''
    SELECT d.id_declinaison, d.stock, c.id_materiau, c.libelle_materiau, d.couleur, a.id_meuble, a.nom_meuble
    FROM declinaison_article d
    JOIN meuble a ON d.meuble_id = a.id_meuble
    JOIN materiau c ON d.materiau_id = c.id_materiau
    WHERE d.id_declinaison = %s
    '''
    mycursor.execute(sql, (id_declinaison_article,))
    declinaison_article = mycursor.fetchone()

    sql = '''
    SELECT DISTINCT couleur
    FROM meuble
    '''
    mycursor.execute(sql)
    couleurs = mycursor.fetchall()

    sql = '''
    SELECT id_materiau, libelle_materiau
    FROM materiau
    '''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()

    d_taille_uniq = declinaison_article['libelle_capacite']
    d_couleur_uniq = declinaison_article['couleur']
    return render_template('admin/article/edit_declinaison_article.html'
                           , tailles=tailles
                           , couleurs=couleurs
                           , declinaison_article=declinaison_article
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['POST'])
def valid_edit_declinaison_article():
    id_declinaison_article = request.form.get('id_declinaison_article', '')
    id_article = request.form.get('id_article', '')
    stock = request.form.get('stock', '')
    taille_id = request.form.get('id_taille', '')
    couleur_id = request.form.get('id_couleur', '')
    mycursor = get_db().cursor()

    sql = '''
    UPDATE declinaison_article
    SET stock = %s, materiau_id = %s, couleur = %s
    WHERE id_declinaison = %s
    '''
    mycursor.execute(sql, (stock, taille_id, couleur_id, id_declinaison_article))
    get_db().commit()

    message = u'declinaison_article modifié , id:' + str(id_declinaison_article) + '- stock :' + str(
        stock) + ' - taille_id:' + str(taille_id) + ' - couleur_id:' + str(couleur_id)
    flash(message, 'alert-success')
    return redirect('/admin/article/edit?id_article=' + str(id_article))


@admin_declinaison_article.route('/admin/declinaison_article/delete', methods=['GET'])
def admin_delete_declinaison_article():
    id_declinaison_article = request.args.get('id_declinaison_article', '')
    id_article = request.args.get('id_article', '')

    mycursor = get_db().cursor()
    sql = '''
    DELETE FROM declinaison_article
    WHERE id_declinaison = %s
    '''
    mycursor.execute(sql, (id_declinaison_article,))
    get_db().commit()

    flash(u'declinaison supprimée, id_declinaison_article : ' + str(id_declinaison_article), 'alert-success')
    return redirect('/admin/article/edit?id_article=' + str(id_article))