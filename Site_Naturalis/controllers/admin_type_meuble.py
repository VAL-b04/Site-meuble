#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_type_meuble = Blueprint('admin_type_meuble', __name__,
                        template_folder='templates')

@admin_type_meuble.route('/admin/type-meuble/show')
def show_type_meuble():
    mycursor = get_db().cursor()
    sql = '''SELECT tm.id_type_meuble, tm.libelle_type_meuble, COUNT(m.id_meuble) as nbr_meubles
    FROM type_meuble tm
    LEFT JOIN meuble m ON tm.id_type_meuble = m.type_meuble_id
    GROUP BY tm.id_type_meuble, tm.libelle_type_meuble
    ORDER BY tm.libelle_type_meuble'''
    mycursor.execute(sql)
    types_meuble = mycursor.fetchall()
    return render_template('admin/type_meuble/show_type_meuble.html', types_meuble=types_meuble)

@admin_type_meuble.route('/admin/type-meuble/add', methods=['GET'])
def add_type_meuble():
    return render_template('admin/type_meuble/add_type_meuble.html')

@admin_type_meuble.route('/admin/type-meuble/add', methods=['POST'])
def valid_add_type_meuble():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = '''INSERT INTO type_meuble (libelle_type_meuble) VALUES (%s)'''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'type ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/type-meuble/show') #url_for('show_type_meuble')

@admin_type_meuble.route('/admin/type-meuble/delete', methods=['GET'])
def delete_type_meuble():
    id_type_meuble = request.args.get('id_type_meuble', '')
    mycursor = get_db().cursor()

    # Vérifier s'il y a des meubles associés à ce type
    sql = '''SELECT COUNT(*) as nb_meubles FROM meuble WHERE type_meuble_id = %s'''
    mycursor.execute(sql, (id_type_meuble,))
    nb_meubles = mycursor.fetchone()

    if nb_meubles['nb_meubles'] > 0:
        message = u'Impossible de supprimer ce type de meuble car il est associé à des meubles'
        flash(message, 'alert-warning')
    else:
        # Supprimer le type de meuble
        sql = '''DELETE FROM type_meuble WHERE id_type_meuble = %s'''
        mycursor.execute(sql, (id_type_meuble,))
        get_db().commit()
        message = u'type meuble supprimé, id : ' + id_type_meuble
        flash(message, 'alert-success')

    return redirect('/admin/type-meuble/show')

@admin_type_meuble.route('/admin/type-meuble/edit', methods=['GET'])
def edit_type_meuble():
    id_type_meuble = request.args.get('id_type_meuble', '')
    mycursor = get_db().cursor()
    sql = '''SELECT id_type_meuble, libelle_type_meuble FROM type_meuble WHERE id_type_meuble = %s'''
    mycursor.execute(sql, (id_type_meuble,))
    type_meuble = mycursor.fetchone()
    return render_template('admin/type_meuble/edit_type_meuble.html', type_meuble=type_meuble)

@admin_type_meuble.route('/admin/type-meuble/edit', methods=['POST'])
def valid_edit_type_meuble():
    libelle = request.form['libelle']
    id_type_meuble = request.form.get('id_type_meuble', '')
    tuple_update = (libelle, id_type_meuble)
    mycursor = get_db().cursor()
    sql = '''UPDATE type_meuble SET libelle_type_meuble = %s WHERE id_type_meuble = %s'''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    flash(u'type meuble modifié, id: ' + id_type_meuble + " libelle : " + libelle, 'alert-success')
    return redirect('/admin/type-meuble/show')








