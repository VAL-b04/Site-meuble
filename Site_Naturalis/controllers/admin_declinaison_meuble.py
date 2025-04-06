#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash, session
from connexion_db import get_db

admin_declinaison_meuble = Blueprint('admin_declinaison_meuble', __name__,
                                    template_folder='templates')


@admin_declinaison_meuble.route('/admin/declinaison_meuble/show')
def admin_declinaison_meuble_show():
    mycursor = get_db().cursor()
    
    # Récupération des meubles qui ont des déclinaisons de matériaux
    sql = '''
        SELECT m.id_meuble, m.nom_meuble, 
               COUNT(dm.id_declinaison_meuble) as nb_declinaisons,
               GROUP_CONCAT(ma.libelle_materiau) as materiaux
        FROM meuble m
        JOIN declinaison_meuble dm ON m.id_meuble = dm.meuble_id
        JOIN materiau ma ON dm.materiau_id = ma.id_materiau
        GROUP BY m.id_meuble, m.nom_meuble
    '''
    mycursor.execute(sql)
    meubles = mycursor.fetchall()
    
    return render_template('admin/declinaison_meuble/show.html',
                         meubles=meubles)


@admin_declinaison_meuble.route('/admin/declinaison_meuble/add', methods=['GET'])
def admin_declinaison_meuble_add():
    mycursor = get_db().cursor()
    
    # Récupération de tous les meubles disponibles
    sql = '''
        SELECT m.id_meuble, m.nom_meuble 
        FROM meuble m
        WHERE m.disponible = 1
        ORDER BY m.nom_meuble
    '''
    mycursor.execute(sql)
    meubles = mycursor.fetchall()
    
    # Récupération des matériaux
    sql = '''
        SELECT id_materiau, libelle_materiau 
        FROM materiau
        ORDER BY libelle_materiau
    '''
    mycursor.execute(sql)
    materiaux = mycursor.fetchall()
    
    return render_template('admin/declinaison_meuble/add.html',
                         meubles=meubles,
                         materiaux=materiaux)


@admin_declinaison_meuble.route('/admin/declinaison_meuble/add', methods=['POST'])
def admin_declinaison_meuble_add_valid():
    mycursor = get_db().cursor()
    
    meuble_id = request.form.get('id_meuble')
    materiau_id = request.form.get('id_materiau')
    prix = request.form.get('prix')
    stock = request.form.get('stock')
    
    # Vérification si la déclinaison existe déjà
    sql = '''
        SELECT * FROM declinaison_meuble
        WHERE meuble_id = %s AND materiau_id = %s
    '''
    mycursor.execute(sql, (meuble_id, materiau_id))
    declinaison_existante = mycursor.fetchone()
    
    if declinaison_existante:
        flash('Cette déclinaison existe déjà pour ce meuble', 'danger')
        return redirect('/admin/declinaison_meuble/add')
    
    # Ajout de la déclinaison
    sql = '''
        INSERT INTO declinaison_meuble (meuble_id, materiau_id, prix_declinaison, stock)
        VALUES (%s, %s, %s, %s)
    '''
    mycursor.execute(sql, (meuble_id, materiau_id, prix, stock))
    get_db().commit()
    
    flash('Déclinaison ajoutée avec succès', 'success')
    return redirect('/admin/declinaison_meuble/show')


@admin_declinaison_meuble.route('/admin/declinaison_meuble/delete', methods=['POST'])
def admin_declinaison_meuble_delete():
    mycursor = get_db().cursor()
    
    id_declinaison = request.form.get('id_declinaison_meuble')
    
    # Vérification si c'est la dernière déclinaison
    sql = '''
        SELECT meuble_id, COUNT(*) as nb_declinaisons
        FROM declinaison_meuble
        WHERE meuble_id = (SELECT meuble_id FROM declinaison_meuble WHERE id_declinaison_meuble = %s)
        GROUP BY meuble_id
    '''
    mycursor.execute(sql, (id_declinaison,))
    result = mycursor.fetchone()
    
    if result['nb_declinaisons'] <= 1:
        flash('Impossible de supprimer la dernière déclinaison d\'un meuble', 'error')
        return redirect('/admin/declinaison_meuble/show')
    
    # Suppression de la déclinaison
    sql = '''
        DELETE FROM declinaison_meuble
        WHERE id_declinaison_meuble = %s
    '''
    mycursor.execute(sql, (id_declinaison,))
    get_db().commit()
    
    flash('Déclinaison supprimée avec succès', 'success')
    return redirect('/admin/declinaison_meuble/show')
