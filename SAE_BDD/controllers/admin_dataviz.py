#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()
    sql = '''
    SELECT t.libelle_type_meuble as libelle, COUNT(c.id_meuble) as nbr_articles
    FROM type_meuble t
    LEFT JOIN meuble c ON t.id_type_meuble = c.type_meuble
    GROUP BY t.id_type_meuble, t.libelle_type_meuble
    '''
    mycursor.execute(sql)
    datas_show = mycursor.fetchall()
    labels = [str(row['libelle']) for row in datas_show]
    values = [int(row['nbr_articles']) for row in datas_show]

    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , datas_show=datas_show
                           , labels=labels
                           , values=values)


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()
    sql = '''
    SELECT LEFT(u.code_postal, 2) as dep, COUNT(*) as nombre
    FROM utilisateur u
    GROUP BY LEFT(u.code_postal, 2)
    '''
    mycursor.execute(sql)
    adresses = mycursor.fetchall()

    maxAddress = max(adresse['nombre'] for adresse in adresses) if adresses else 0
    if maxAddress != 0:
        for element in adresses:
            indice = element['nombre'] / maxAddress
            element['indice'] = round(indice,2)

    print(adresses)

    return render_template('admin/dataviz/dataviz_etat_map.html'
                           , adresses=adresses
                          )