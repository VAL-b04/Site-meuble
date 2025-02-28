#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = '''  SELECT nom_meuble, id_meuble, libelle_type_meuble, type_meuble.id_type_meuble AS type_id, prix_meuble, meuble.stock, 
               COUNT(declinaison_meuble.id_declinaison_meuble) AS nb_declinaisons, meuble.image AS image_meuble
        FROM meuble
        JOIN type_meuble ON meuble.id_type = type_meuble.id_type_meuble
        LEFT JOIN declinaison_meuble ON meuble.id_meuble = declinaison_meuble.meuble_id
        GROUP BY meuble.id_meuble;
        '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    return render_template('admin/article/show_article.html', articles=articles)


@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()
    sql = '''
            SELECT id_type_meuble AS type_article_id, libelle_type_meuble FROM type_meuble;
            '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()


    return render_template('admin/article/add_article.html'
                           ,types_article=types_article,
                           #,couleurs=colors
                           #,tailles=tailles
                            )


@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')


    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None



    sql = '''  INSERT INTO meuble (nom_meuble, id_type, prix_meuble, image, fournisseur) 
    VALUES (%s, %s, %s, %s, %s) '''

    tuple_add = (nom, type_article_id, prix, filename, description)
    print(tuple_add)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'article ajouté , nom: ', nom, ' - type_article:', type_article_id, ' - prix:', prix,
          ' - description:', description, ' - image:', image)
    message = u'article ajouté , nom:' + nom + '- type_article:' + type_article_id + ' - prix:' + prix + ' - description:' + description + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    # 1. Vérifier s'il y a des déclinaisons pour cet article
    sql = '''SELECT COUNT(*) AS nb_declinaison FROM declinaison_meuble WHERE meuble_id = %s'''
    mycursor.execute(sql, (id_article,))
    nb_declinaison = mycursor.fetchone()

    if nb_declinaison['nb_declinaison'] > 0:
        message = u'il y a des déclinaisons dans cet article : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        # 2. Récupérer l'image de l'article
        sql = '''SELECT image FROM meuble WHERE id_meuble = %s'''
        mycursor.execute(sql, (id_article,))
        article = mycursor.fetchone()

        if article:
            image = article['image']
        else:
            image = None

        # 3. Supprimer les déclinaisons de l'article
        sql = '''DELETE FROM declinaison_meuble WHERE meuble_id = %s'''
        mycursor.execute(sql, (id_article,))

        # 4. Supprimer l'article (meuble)
        sql = '''DELETE FROM meuble WHERE id_meuble = %s'''
        mycursor.execute(sql, (id_article,))

        get_db().commit()

        # 5. Supprimer l'image du fichier système si elle existe
        if image:
            try:
                os.remove('static/images/' + image)
            except FileNotFoundError:
                print(f"Image {image} non trouvée sur le serveur.")

        print("Un article supprimé, id :", id_article)
        message = u'un article supprimé, id : ' + str(id_article)
        flash(message, 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''
    SELECT id_meuble, nom_meuble AS nom, id_type, prix_meuble AS prix, stock, image, description
    FROM meuble
    WHERE id_meuble = %s;
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    print(article)
    sql = '''
    SELECT id_type_meuble, libelle_type_meuble AS libelle
    FROM type_meuble;

    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    # sql = '''
    # requête admin_article_6
    # '''
    # mycursor.execute(sql, id_article)
    # declinaisons_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html'
                           ,article=article
                           ,types_article=types_article
                         #  ,declinaisons_article=declinaisons_article
                           )


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id', '')
    stock = request.form.get('stock')
    prix = request.form.get('prix', '')
    description = request.form.get('description')
    sql = '''
       SELECT image
FROM meuble
WHERE id_meuble = %s;
       '''
    mycursor.execute(sql, id_article)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename

    sql = '''  UPDATE meuble
SET nom_meuble = %s, image = %s, prix_meuble = %s, id_type = %s, description = %s, stock = %s
WHERE id_meuble = %s;
 '''
    mycursor.execute(sql, (nom, image_nom, prix, type_article_id, description, stock, id_article))

    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'article modifié , nom:' + nom + '- type_article :' + type_article_id + ' - prix:' + prix + ' - stock:' + stock  + ' - image:' + image_nom + ' - description: ' + description
    flash(message, 'alert-success')
    return redirect('/admin/article/show')







@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article=[]
    commentaires = {}
    return render_template('admin/article/show_avis.html'
                           , article=article
                           , commentaires=commentaires
                           )


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    userId = request.form.get('idUser', None)

    return admin_avis(article_id)
