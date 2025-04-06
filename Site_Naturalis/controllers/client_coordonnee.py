#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__,
                        template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    utilisateur=[]
    nb_adresses = 0

    sql = '''
    SELECT login, nom_utilisateur as nom, email
    FROM utilisateur WHERE id_utilisateur = %s
    '''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    # Récupérer toutes les adresses de l'utilisateur
    sql = '''
    SELECT a.*, a.nom_adresse as nom, 
           (SELECT COUNT(*) FROM commande c 
            WHERE c.adresse_id_livr = a.id_adresse OR c.adresse_id_fact = a.id_adresse) as nb_commandes
    FROM adresse a
    JOIN concerne ON a.id_adresse = concerne.adresse_id
    WHERE concerne.utilisateur_id = %s 
    '''
    mycursor.execute(sql, id_client)
    adresses = mycursor.fetchall()
    
    # Compter le nombre d'adresses valides de l'utilisateur
    sql = '''
    SELECT COUNT(*) as nb_adresses
    FROM adresse
    JOIN concerne ON adresse.id_adresse = concerne.adresse_id
    WHERE utilisateur_id = %s and valide = '1'
    '''
    mycursor.execute(sql, id_client)
    nb_adresses = mycursor.fetchone()
    nb_adresses = nb_adresses['nb_adresses']
    
    # Identifier l'adresse favorite (la dernière utilisée dans une commande)
    sql = '''
    SELECT adresse_id_livr as id_adresse_favorite
    FROM commande
    WHERE utilisateur_id = %s
    ORDER BY date_achat DESC
    LIMIT 1
    '''
    mycursor.execute(sql, id_client)
    adresse_favorite = mycursor.fetchone()
    
    # Si aucune commande, prend la dernière adresse enregistré
    if adresse_favorite is None:
        sql = '''
        SELECT id_adresse as id_adresse_favorite
        FROM adresse
        JOIN concerne ON adresse.id_adresse = concerne.adresse_id
        WHERE utilisateur_id = %s AND valide = '1'
        ORDER BY id_adresse DESC
        LIMIT 1
        '''
        mycursor.execute(sql, id_client)
        adresse_favorite = mycursor.fetchone()

    return render_template('client/coordonnee/show_coordonnee.html'
                           , utilisateur=utilisateur
                           , adresses=adresses
                           , nb_adresses=nb_adresses
                           , adresse_favorite=adresse_favorite
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
    SELECT login, nom_utilisateur as nom, email
    FROM utilisateur
    WHERE id_utilisateur = %s
    '''
    mycursor.execute(sql,id_client)
    utilisateur=mycursor.fetchone()

    return render_template('client/coordonnee/edit_coordonnee.html'
                           ,utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom=request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')
    utilisateur = []

    # Verifie si le login ou email existe deja pour un autre utilisateur
    sql = '''
    SELECT *
    FROM utilisateur
    WHERE (login = %s OR email = %s) AND id_utilisateur != %s
    '''
    tuple = (login, email, id_client)
    mycursor.execute(sql,tuple)
    user = mycursor.fetchone()
    print("user = " + str(user))
    
    if user:
        flash(u'Le login ou l\'email existe déjà pour un autre utilisateur', 'alert-warning')
        return redirect('/client/coordonnee/edit')
    
    sql = '''
    UPDATE utilisateur
    SET nom_utilisateur = %s, login = %s, email = %s
    WHERE id_utilisateur = %s;
    '''
    tuple = (nom,login,email,id_client)
    mycursor.execute(sql,tuple)
    get_db().commit()

    session['login'] = login
    session['nom'] = nom
    
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse',methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse= request.form.get('id_adresse')

    # Verifie si l'adresse est l'adresse favorite
    sql = '''
    SELECT adresse_id_livr as id_adresse_favorite
    FROM commande
    WHERE utilisateur_id = %s
    ORDER BY date_achat DESC
    LIMIT 1
    '''
    mycursor.execute(sql, id_client)
    adresse_favorite = mycursor.fetchone()
    est_adresse_favorite = adresse_favorite is not None and adresse_favorite['id_adresse_favorite'] == int(id_adresse)

    # Verifie si l'adresse est dans une commande
    sql = '''
    SELECT *
    FROM commande
    WHERE adresse_id_livr = %s OR adresse_id_fact = %s
    '''
    tuple = (id_adresse,id_adresse)
    mycursor.execute(sql,tuple)
    adresse_block = mycursor.fetchone()
    
    # Si l adresse est dans une commande, on la désactive
    if adresse_block:
        flash(u'Cette adresse est actuellement dans une commande','alert-warning')
        
        sql = '''
        UPDATE adresse
        SET valide = '0'
        WHERE id_adresse = %s
        '''
        mycursor.execute(sql,id_adresse)
        get_db().commit()
    else:
        # Sinon on la supprime dans concerne en premier pour pouvoir la supprimer dans adresse   
        sql = '''
        DELETE FROM concerne
        WHERE adresse_id = %s
        '''
        mycursor.execute(sql,id_adresse)
        get_db().commit()

        sql = '''
        DELETE FROM adresse
        WHERE id_adresse = %s
        '''
        mycursor.execute(sql,id_adresse)
        get_db().commit()
    
    # Si l adresse supprime était l'adresse favorite, definir une nouvelle adresse favorite
    if est_adresse_favorite:
        # Trouver la derniere adresse valide utilise dans une commande
        sql = '''
        SELECT adresse_id_livr as id_adresse_favorite
        FROM commande
        WHERE utilisateur_id = %s AND adresse_id_livr != %s
        ORDER BY date_achat DESC
        LIMIT 1
        '''
        mycursor.execute(sql, (id_client, id_adresse))
        nouvelle_favorite = mycursor.fetchone()
        
        # Si aucune autre adresse n'a été utilise, prendre la première adresse valide
        if nouvelle_favorite is None:
            sql = '''
            SELECT id_adresse as id_adresse_favorite
            FROM adresse
            JOIN concerne ON adresse.id_adresse = concerne.adresse_id
            WHERE utilisateur_id = %s AND valide = '1' AND id_adresse != %s
            LIMIT 1
            '''
            mycursor.execute(sql, (id_client, id_adresse))
            nouvelle_favorite = mycursor.fetchone()

    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
    SELECT nom_utilisateur as nom, login
    FROM adresse
    JOIN concerne ON adresse.id_adresse = concerne.adresse_id
    JOIN utilisateur ON concerne.utilisateur_id = utilisateur.id_utilisateur
    WHERE utilisateur_id = %s
    '''

    mycursor.execute(sql,id_client)
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html'
                           ,utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/add_adresse',methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')

    # Verifier que le code postal est compose de 5 chiffres
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash(u'Le code postal doit être composé de 5 chiffres', 'alert-warning')
        return redirect('/client/coordonnee/add_adresse')

    # Ne pas ajouter d adresse si l'utilisateur en a déjà quatres
    sql = '''
    SELECT COUNT(*) as nb_adresses
    FROM adresse
    JOIN concerne ON adresse.id_adresse = concerne.adresse_id
    WHERE utilisateur_id = %s and valide = '1'
    '''
    mycursor.execute(sql,id_client)
    nb_adresses = mycursor.fetchone()
    print(nb_adresses)
    if nb_adresses['nb_adresses'] >= 4:
        flash(u'Vous avez déjà quatres adresses', 'alert-warning')
        return redirect('/client/coordonnee/show')
    
    # Verifie si c'est la première adresse de l'utilisateur
    sql = '''
    SELECT COUNT(*) as nb_adresses
    FROM adresse
    JOIN concerne ON adresse.id_adresse = concerne.adresse_id
    WHERE utilisateur_id = %s
    '''
    mycursor.execute(sql,id_client)
    premiere_adresse = mycursor.fetchone()
    est_premiere_adresse = premiere_adresse['nb_adresses'] == 0

    sql = '''
    INSERT INTO adresse(nom_adresse, rue, code_postal, ville, valide)
    VALUES (%s, %s, %s, %s, 1)
    '''
    mycursor.execute(sql, (nom, rue, code_postal, ville))
    id_adresse = mycursor.lastrowid
    get_db().commit()

    sql = '''
    INSERT INTO concerne(utilisateur_id, adresse_id)
    VALUES (%s, %s)
    '''
    mycursor.execute(sql, (id_client, id_adresse))
    get_db().commit()
    
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')

    # Verifie si l'adresse est actuellement dans une commande
    sql = '''
    SELECT *
    FROM commande
    WHERE (adresse_id_livr = %s OR adresse_id_fact = %s)
    '''
    tuple = (id_adresse,id_adresse)
    mycursor.execute(sql,tuple)
    adresse_block = mycursor.fetchone()
    
    if adresse_block:
        flash(u'Cette adresse est actuellement dans une commande, elle ne peut pas être modifiée','alert-warning')
        return redirect('/client/coordonnee/show')

    sql = '''
    SELECT nom_adresse AS nom,code_postal,ville,rue,id_adresse
    FROM adresse
    WHERE id_adresse = %s
    '''
    mycursor.execute(sql,id_adresse)
    adresse = mycursor.fetchone()
    
    sql = '''
    SELECT *
    FROM utilisateur
    WHERE id_utilisateur = %s
    '''
    mycursor.execute(sql,id_client)
    utilisateur = mycursor.fetchone()

    return render_template('/client/coordonnee/edit_adresse.html'
                           ,utilisateur=utilisateur
                           ,adresse=adresse
                           )

@client_coordonnee.route('/client/coordonnee/edit_adresse',methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')

    # Verifie que le code postal est composé de 5 chiffres
    if not code_postal.isdigit() or len(code_postal) != 5:
        flash(u'Le code postal doit être composé de 5 chiffres', 'alert-warning')
        return redirect('/client/coordonnee/edit_adresse?id_adresse=' + id_adresse)

    sql = '''
    UPDATE adresse
    SET nom_adresse = %s, code_postal = %s, ville = %s, rue = %s
    WHERE id_adresse = %s;
    '''
    tuple = (nom,code_postal,ville,rue,id_adresse)
    print(tuple)
    mycursor.execute(sql,tuple)
    get_db().commit()
    
    return redirect('/client/coordonnee/show')
