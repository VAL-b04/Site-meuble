#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash, url_for
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_meuble = Blueprint('admin_meuble', __name__,
                          template_folder='templates')


@admin_meuble.route('/admin/meuble/show')
def admin_meuble_show():
    mycursor = get_db().cursor()
    sql = '''
    SELECT m.*, 
           tm.libelle_type_meuble,
           COUNT(DISTINCT c.utilisateur_id) as nb_commentaires,
           COUNT(DISTINCT n.utilisateur_id) as nb_avis,
           COALESCE(AVG(n.note), 0) as moyenne_notes
    FROM meuble m
    LEFT JOIN type_meuble tm ON m.type_meuble_id = tm.id_type_meuble
    LEFT JOIN commentaire c ON m.id_meuble = c.meuble_id
    LEFT JOIN note n ON m.id_meuble = n.meuble_id
    GROUP BY m.id_meuble, m.nom_meuble, m.disponible, m.prix_meuble, 
             m.description_meuble, m.image_meuble, m.type_meuble_id,
             tm.libelle_type_meuble
    ORDER BY m.id_meuble DESC
    '''
    mycursor.execute(sql)
    meubles = mycursor.fetchall()
    return render_template('admin/meuble/show_meuble.html', meubles=meubles)


@admin_meuble.route('/admin/meuble/add', methods=['GET'])
def add_meuble():
    mycursor = get_db().cursor()

    sql = '''
        SELECT id_type_meuble, libelle_type_meuble
        FROM type_meuble
        ORDER BY libelle_type_meuble
        '''

    mycursor.execute(sql)
    type_meuble = mycursor.fetchall()

    return render_template('admin/meuble/add_meuble.html'
                           ,types_meuble=type_meuble,
                           #,couleurs=colors
                           #,tailles=tailles
                            )


@admin_meuble.route('/admin/meuble/add', methods=['POST'])
def valid_add_meuble():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_meuble_id = request.form.get('type_meuble_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')

    # Validation des champs requis
    if not nom or not type_meuble_id or not prix or not description:
        message = u'Veuillez remplir tous les champs obligatoires'
        flash(message, 'alert-warning')
        return redirect('/admin/meuble/add')

    try:
        # Conversion des valeurs en types appropriés
        type_meuble_id = int(type_meuble_id)
        prix = float(prix)

        if image:
            filename = 'img_upload_'+ str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
        else:
            filename = None

        sql = '''  INSERT INTO meuble (nom_meuble, image_meuble, prix_meuble, type_meuble_id, description_meuble, disponible)
        VALUES (%s, %s, %s, %s, %s, 1)'''

        tuple_add = (nom, filename, prix, type_meuble_id, description)
        print(tuple_add)
        mycursor.execute(sql, tuple_add)
        get_db().commit()

        print(u'meuble ajouté , nom: ', nom, ' - type_meuble:', type_meuble_id, ' - prix:', prix,
              ' - description:', description, ' - image:', image)
        message = u'meuble ajouté , nom:' + nom + '- type_meuble:' + str(type_meuble_id) + ' - prix:' + str(prix) + ' - description:' + description + ' - image:' + str(
            image)
        flash(message, 'alert-success')
    except ValueError:
        message = u'Erreur de format dans les données saisies'
        flash(message, 'alert-danger')
    except Exception as e:
        message = u'Une erreur est survenue lors de l\'ajout du meuble'
        flash(message, 'alert-danger')
        print("Erreur:", str(e))

    return redirect('/admin/meuble/show')


@admin_meuble.route('/admin/meuble/delete', methods=['GET'])
def delete_meuble():
    id_meuble=request.args.get('id_meuble')
    mycursor = get_db().cursor()
    
    # Vérifier s'il y a des déclinaisons
    sql = '''
    SELECT COUNT(*) as nb_declinaison
    FROM declinaison_meuble
    WHERE meuble_id = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    nb_declinaison = mycursor.fetchone()
    
    if nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans cet meuble : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        # Récupérer l'image du meuble
        sql = '''
        SELECT image_meuble
        FROM meuble
        WHERE id_meuble = %s
        '''
        mycursor.execute(sql, (id_meuble,))
        meuble = mycursor.fetchone()
        
        # Supprimer le meuble
        sql = '''
        DELETE FROM meuble
        WHERE id_meuble = %s
        '''
        mycursor.execute(sql, (id_meuble,))
        get_db().commit()
        
        # Supprimer l'image si elle existe
        if meuble['image_meuble'] and os.path.exists(os.path.join('static/images/', meuble['image_meuble'])):
            os.remove(os.path.join('static/images/', meuble['image_meuble']))

        message = u'un meuble supprimé, id : ' + id_meuble
        flash(message, 'alert-success')

    return redirect('/admin/meuble/show')


@admin_meuble.route('/admin/meuble/edit', methods=['GET'])
def edit_meuble():
    id_meuble=request.args.get('id_meuble')
    mycursor = get_db().cursor()
    
    # Récupérer les informations du meuble
    sql = '''
    SELECT m.id_meuble, m.nom_meuble, m.image_meuble, m.prix_meuble, 
           m.type_meuble_id, m.description_meuble, m.disponible,
           tm.libelle_type_meuble
    FROM meuble m
    LEFT JOIN type_meuble tm ON m.type_meuble_id = tm.id_type_meuble
    WHERE m.id_meuble = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    meuble = mycursor.fetchone()

    # Récupérer tous les types de meubles pour le select
    sql_types = '''
    SELECT id_type_meuble, libelle_type_meuble
    FROM type_meuble
    ORDER BY libelle_type_meuble
    '''
    mycursor.execute(sql_types)
    types_meuble = mycursor.fetchall()

    return render_template('admin/meuble/edit_meuble.html',
                         meuble=meuble,
                         types_meuble=types_meuble)


@admin_meuble.route('/admin/meuble/edit', methods=['POST'])
def valid_edit_meuble():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_meuble = request.form.get('id_meuble', '')
    image = request.files.get('image', '')
    type_meuble_id = request.form.get('type_meuble_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description')
    stock = request.form.get('stock', '0')

    # Récupérer l'image actuelle
    sql_image = '''
        SELECT image_meuble
        FROM meuble 
        WHERE id_meuble = %s;
    '''
    mycursor.execute(sql_image, (id_meuble,))
    image_nom = mycursor.fetchone()
    if image_nom:
        image_nom = image_nom['image_meuble']

    # Gérer la nouvelle image si une est uploadée
    if image:
        if image_nom and os.path.exists(os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
        image_nom = filename

    # Mise à jour du meuble
    sql_update = '''  
        UPDATE meuble 
        SET nom_meuble = %s, image_meuble = %s, prix_meuble = %s, type_meuble_id = %s, 
            description_meuble = %s, disponible = %s
        WHERE id_meuble = %s;
    '''
    mycursor.execute(sql_update, (nom, image_nom, prix, type_meuble_id, description, stock, id_meuble))
    get_db().commit()

    message = u'Meuble modifié - Nom: ' + nom + ' - Type de meuble: ' + type_meuble_id + ' - Prix: ' + prix + ' - Image: ' + str(image_nom) + ' - Description: ' + description + ' - Stock: ' + stock
    flash(message, 'alert-success')
    return redirect('/admin/meuble/show')


@admin_meuble.route('/admin/meuble/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    meuble=[]
    commentaires = {}
    return render_template('admin/meuble/show_avis.html'
                           , meuble=meuble
                           , commentaires=commentaires
                           )


@admin_meuble.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    meuble_id = request.form.get('idmeuble', None)
    userId = request.form.get('idUser', None)

    return admin_avis(meuble_id)


@admin_meuble.route('/admin/meuble/commentaires')
def admin_meuble_commentaires():
    id_meuble = request.args.get('id_meuble')
    mycursor = get_db().cursor()
    
    # Récupérer les informations du meuble
    sql_meuble = '''
    SELECT m.*, tm.libelle_type_meuble
    FROM meuble m
    LEFT JOIN type_meuble tm ON m.type_meuble_id = tm.id_type_meuble
    WHERE m.id_meuble = %s
    '''
    mycursor.execute(sql_meuble, (id_meuble,))
    meuble = mycursor.fetchone()

    # Récupérer les commentaires avec les informations des utilisateurs
    sql_commentaires = '''
    SELECT c.*, u.nom_utilisateur as nom, u.login
    FROM commentaire c
    JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
    WHERE c.meuble_id = %s
    ORDER BY c.date_publication ASC
    '''
    mycursor.execute(sql_commentaires, (id_meuble,))
    commentaires = mycursor.fetchall()

    return render_template('admin/meuble/show_meuble_commentaires.html',
                         meuble=meuble,
                         commentaires=commentaires)


@admin_meuble.route('/admin/meuble/commentaires/valider')
def admin_meuble_commentaires_valider():
    id_meuble = request.args.get('id_meuble')
    mycursor = get_db().cursor()
    
    # Valider tous les commentaires du meuble
    sql = '''
    UPDATE commentaire 
    SET valider = 1 
    WHERE meuble_id = %s AND valider = 0
    '''
    mycursor.execute(sql, (id_meuble,))
    get_db().commit()
    
    message = u'Tous les commentaires ont été validés'
    flash(message, 'alert-success')
    
    return redirect('/admin/meuble/commentaires?id_meuble=' + id_meuble)


@admin_meuble.route('/admin/meuble/commentaires/repondre', methods=['GET'])
def admin_meuble_commentaires_repondre():
    id_meuble = request.args.get('id_meuble')
    id_utilisateur = request.args.get('id_utilisateur')
    date_publication = request.args.get('date_publication')
    
    return render_template('admin/meuble/add_commentaire.html',
                         id_meuble=id_meuble,
                         id_utilisateur=id_utilisateur,
                         date_publication=date_publication)

@admin_meuble.route('/admin/meuble/commentaires/repondre', methods=['POST'])
def admin_meuble_commentaires_repondre_valid():
    id_meuble = request.form.get('id_meuble')
    commentaire = request.form.get('commentaire')
    mycursor = get_db().cursor()
    
    # Insérer la réponse en tant qu'administrateur (id_utilisateur = 1)
    sql = '''
    INSERT INTO commentaire (utilisateur_id, meuble_id, date_publication, commentaire, valider)
    VALUES (%s, %s, NOW(), %s, 1)
    '''
    mycursor.execute(sql, (1, id_meuble, commentaire))
    get_db().commit()
    
    message = u'Votre réponse a été ajoutée'
    flash(message, 'alert-success')
    
    return redirect('/admin/meuble/commentaires?id_meuble=' + id_meuble)

@admin_meuble.route('/admin/meuble/commentaires/delete', methods=['POST'])
def admin_meuble_commentaires_delete():
    id_meuble = request.form.get('id_meuble')
    id_utilisateur = request.form.get('id_utilisateur')
    date_publication = request.form.get('date_publication')
    mycursor = get_db().cursor()
    
    # Supprimer le commentaire
    sql = '''
    DELETE FROM commentaire 
    WHERE meuble_id = %s 
    AND utilisateur_id = %s 
    AND date_publication = %s
    '''
    mycursor.execute(sql, (id_meuble, id_utilisateur, date_publication))
    get_db().commit()
    
    message = u'Le commentaire a été supprimé'
    flash(message, 'alert-success')
    
    return redirect('/admin/meuble/commentaires?id_meuble=' + id_meuble)

@admin_meuble.route('/admin/meuble/stock')
def admin_meuble_stock():
    mycursor = get_db().cursor()
    
    # Récupération des meubles avec leurs déclinaisons et stocks
    sql = '''
    SELECT m.id_meuble, m.nom_meuble,
           COUNT(DISTINCT dm.id_declinaison_meuble) as nb_declinaisons,
           SUM(dm.stock) as stock_total,
           GROUP_CONCAT(
               DISTINCT CONCAT(dm.id_declinaison_meuble, ':', ma.libelle_materiau, ' (', dm.stock, ')')
               SEPARATOR '|'
           ) as details_stock,
           COUNT(DISTINCT lc.commande_id) as nb_commandes,
           MIN(dm.stock) as stock_min,
           CASE WHEN MIN(dm.stock) = 0 THEN 1 ELSE 0 END as alerte_stock
    FROM meuble m
    LEFT JOIN declinaison_meuble dm ON m.id_meuble = dm.meuble_id
    LEFT JOIN materiau ma ON dm.materiau_id = ma.id_materiau
    LEFT JOIN ligne_commande lc ON dm.id_declinaison_meuble = lc.declinaison_meuble_id
    GROUP BY m.id_meuble, m.nom_meuble
    ORDER BY m.nom_meuble
    '''
    mycursor.execute(sql)
    meubles = mycursor.fetchall()
    
    # Formatage des détails du stock
    for meuble in meubles:
        if meuble['details_stock']:
            details = []
            for detail in meuble['details_stock'].split('|'):
                id_declinaison, reste = detail.split(':', 1)
                details.append({
                    'id': id_declinaison,
                    'detail': reste
                })
            meuble['details_stock'] = details
        else:
            meuble['details_stock'] = []
    
    return render_template('admin/meuble/stock.html', meubles=meubles)


@admin_meuble.route('/admin/meuble/declinaison/<int:id_meuble>')
def admin_meuble_declinaison(id_meuble):
    mycursor = get_db().cursor()
    
    # Récupération des informations du meuble
    sql = '''
    SELECT m.*, tm.libelle_type_meuble
    FROM meuble m
    LEFT JOIN type_meuble tm ON m.type_meuble_id = tm.id_type_meuble
    WHERE m.id_meuble = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    meuble = mycursor.fetchone()
    
    # Récupération des déclinaisons du meuble
    sql = '''
    SELECT 
        dm.id_declinaison_meuble,
        dm.stock,
        dm.prix_declinaison,
        dm.is_unique,
        mat.libelle_materiau,
        mat.id_materiau,
        (SELECT COUNT(*) FROM ligne_commande lc WHERE lc.declinaison_meuble_id = dm.id_declinaison_meuble) as nb_commandes
    FROM declinaison_meuble dm
    JOIN materiau mat ON dm.materiau_id = mat.id_materiau
    WHERE dm.meuble_id = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    declinaisons = mycursor.fetchall()
    
    # Récupération des matériaux disponibles
    sql = '''
    SELECT id_materiau, libelle_materiau
    FROM materiau
    WHERE id_materiau NOT IN (
        SELECT materiau_id FROM declinaison_meuble WHERE meuble_id = %s
    )
    '''
    mycursor.execute(sql, (id_meuble,))
    materiaux_disponibles = mycursor.fetchall()
    
    return render_template('admin/meuble/declinaison.html', 
                          meuble=meuble, 
                          declinaisons=declinaisons,
                          materiaux_disponibles=materiaux_disponibles)


@admin_meuble.route('/admin/meuble/declinaison/update_stock', methods=['POST'])
def admin_meuble_update_stock():
    mycursor = get_db().cursor()
    
    id_declinaison = request.form.get('id_declinaison_meuble')
    nouveau_stock = request.form.get('stock')
    
    # Mise à jour du stock
    sql = '''
    UPDATE declinaison_meuble
    SET stock = %s
    WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql, (nouveau_stock, id_declinaison))
    get_db().commit()
    
    flash('Stock mis à jour avec succès', 'success')
    
    # Récupération de l'ID du meuble pour la redirection
    sql = '''
    SELECT meuble_id
    FROM declinaison_meuble
    WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql, (id_declinaison,))
    result = mycursor.fetchone()
    
    return redirect(f'/admin/meuble/declinaison/{result["meuble_id"]}')


@admin_meuble.route('/admin/meuble/declinaison/add', methods=['POST'])
def admin_meuble_add_declinaison():
    mycursor = get_db().cursor()
    
    id_meuble = request.form.get('id_meuble')
    id_materiau = request.form.get('id_materiau')
    prix = request.form.get('prix')
    stock = request.form.get('stock')
    is_unique = request.form.get('is_unique', '0')
    
    # Vérification si la déclinaison existe déjà
    sql = '''
    SELECT * FROM declinaison_meuble
    WHERE meuble_id = %s AND materiau_id = %s
    '''
    mycursor.execute(sql, (id_meuble, id_materiau))
    declinaison_existante = mycursor.fetchone()
    
    if declinaison_existante:
        flash('Cette déclinaison existe déjà pour ce meuble', 'error')
        return redirect(f'/admin/meuble/declinaison/{id_meuble}')
    
    # Si c'est une déclinaison unique, vérifier qu'il n'y a pas déjà une autre déclinaison
    if is_unique == '1':
        sql = '''
        SELECT COUNT(*) as nb_declinaisons
        FROM declinaison_meuble
        WHERE meuble_id = %s
        '''
        mycursor.execute(sql, (id_meuble,))
        result = mycursor.fetchone()
        
        if result['nb_declinaisons'] > 0:
            flash('Impossible d\'ajouter une déclinaison unique car il existe déjà des déclinaisons pour ce meuble', 'error')
            return redirect(f'/admin/meuble/declinaison/{id_meuble}')
    
    # Ajout de la déclinaison
    sql = '''
    INSERT INTO declinaison_meuble (meuble_id, materiau_id, prix_declinaison, stock, is_unique)
    VALUES (%s, %s, %s, %s, %s)
    '''
    mycursor.execute(sql, (id_meuble, id_materiau, prix, stock, is_unique))
    get_db().commit()
    
    flash('Déclinaison ajoutée avec succès', 'success')
    return redirect(f'/admin/meuble/declinaison/{id_meuble}')


@admin_meuble.route('/admin/meuble/declinaison/delete', methods=['POST'])
def admin_meuble_delete_declinaison():
    mycursor = get_db().cursor()
    
    id_declinaison = request.form.get('id_declinaison_meuble')
    
    # Vérification si la déclinaison a été commandée
    sql = '''
    SELECT COUNT(*) as nb_commandes
    FROM ligne_commande
    WHERE declinaison_meuble_id = %s
    '''
    mycursor.execute(sql, (id_declinaison,))
    result = mycursor.fetchone()
    
    if result['nb_commandes'] > 0:
        flash('Impossible de supprimer cette déclinaison car elle a déjà été commandée', 'error')
        return redirect('/admin/meuble/stock')
    
    # Récupération de l'ID du meuble pour la redirection
    sql = '''
    SELECT meuble_id, is_unique
    FROM declinaison_meuble
    WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql, (id_declinaison,))
    declinaison = mycursor.fetchone()
    
    # Si c'est une déclinaison unique, vérifier qu'il n'y a pas d'autres déclinaisons
    if declinaison['is_unique']:
        sql = '''
        SELECT COUNT(*) as nb_declinaisons
        FROM declinaison_meuble
        WHERE meuble_id = %s
        '''
        mycursor.execute(sql, (declinaison['meuble_id'],))
        result = mycursor.fetchone()
        
        if result['nb_declinaisons'] > 1:
            flash('Impossible de supprimer cette déclinaison unique car il existe d\'autres déclinaisons', 'error')
            return redirect(f'/admin/meuble/declinaison/{declinaison["meuble_id"]}')
    
    # Suppression de la déclinaison
    sql = '''
    DELETE FROM declinaison_meuble
    WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql, (id_declinaison,))
    get_db().commit()
    
    flash('Déclinaison supprimée avec succès', 'success')
    return redirect(f'/admin/meuble/declinaison/{declinaison["meuble_id"]}')

@admin_meuble.route('/admin/meuble/stock/update', methods=['POST'])
def admin_meuble_stock_update():
    mycursor = get_db().cursor()
    
    id_declinaison = request.form.get('id_declinaison')
    nouveau_stock = request.form.get('stock')
    
    # Vérification que le stock est un nombre positif
    try:
        nouveau_stock = int(nouveau_stock)
        if nouveau_stock < 0:
            flash('Le stock ne peut pas être négatif', 'alert-danger')
            return redirect(url_for('admin_meuble.admin_meuble_stock'))
    except ValueError:
        flash('Le stock doit être un nombre entier', 'alert-danger')
        return redirect(url_for('admin_meuble.admin_meuble_stock'))
    
    # Mise à jour du stock
    sql = '''
    UPDATE declinaison_meuble
    SET stock = %s
    WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql, (nouveau_stock, id_declinaison))
    get_db().commit()
    
    flash('Stock mis à jour avec succès', 'alert-success')
    return redirect(url_for('admin_meuble.admin_meuble_stock'))

@admin_meuble.route('/admin/meuble/stock/delete', methods=['POST'])
def admin_meuble_stock_delete():
    mycursor = get_db().cursor()
    
    id_meuble = request.form.get('id_meuble')
    
    # Vérification si le meuble a des commandes
    sql = '''
    SELECT COUNT(*) as nb_commandes
    FROM ligne_commande lc
    JOIN declinaison_meuble dm ON lc.declinaison_meuble_id = dm.id_declinaison_meuble
    WHERE dm.meuble_id = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    result = mycursor.fetchone()
    
    if result['nb_commandes'] > 0:
        flash('Impossible de supprimer le stock d\'un meuble qui a des commandes', 'alert-danger')
        return redirect(url_for('admin_meuble.admin_meuble_stock'))
    
    # Suppression des déclinaisons
    sql = '''
    DELETE FROM declinaison_meuble
    WHERE meuble_id = %s
    '''
    mycursor.execute(sql, (id_meuble,))
    get_db().commit()
    
    flash('Stock supprimé avec succès', 'alert-danger')
    return redirect(url_for('admin_meuble.admin_meuble_stock'))
