from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from connexion_db import get_db

client_article = Blueprint('client_article', __name__, template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')
def client_article_show():
    mycursor = get_db().cursor()
    id_client = session.get('id_user')

    if not id_client:
        flash(u'Veuillez vous connecter pour accéder à cette page', 'warning')
        return redirect(url_for('auth.login'))

    try:
        sql = '''
        SELECT c.id_meuble, c.nom_meuble, c.prix_meuble, c.photo_url, c.stock, c.description, t.libelle_type_meuble, t.id_type_meuble
        FROM meuble c
        LEFT JOIN type_meuble t ON c.type_meuble = t.id_type_meuble
        '''
        params = []

        filter_conditions = []
        if session.get('filter_word'):
            filter_conditions.append("c.nom_meuble LIKE %s")
            params.append(f"%{session['filter_word']}%")
        if session.get('filter_types'):
            filter_conditions.append(
                "t.id_type_meuble IN ({})".format(','.join(['%s'] * len(session['filter_types']))))
            params.extend(session['filter_types'])
        if session.get('filter_prix_min'):
            filter_conditions.append("c.prix_meuble >= %s")
            params.append(session['filter_prix_min'])
        if session.get('filter_prix_max'):
            filter_conditions.append("c.prix_meuble <= %s")
            params.append(session['filter_prix_max'])

        if filter_conditions:
            sql += " WHERE " + " AND ".join(filter_conditions)

        current_app.logger.info(f"SQL Query: {sql}")
        current_app.logger.info(f"SQL Parameters: {params}")

        mycursor.execute(sql, tuple(params))
        articles = mycursor.fetchall()

        current_app.logger.info(f"Nombre d'articles récupérés : {len(articles)}")

        if not articles:
            current_app.logger.warning("Aucun article trouvé dans la base de données.")
            flash(u'Aucun article disponible pour le moment.', 'info')

        sql = '''
        SELECT id_type_meuble, libelle_type_meuble
        FROM type_meuble
        '''
        mycursor.execute(sql)
        types_article = mycursor.fetchall()

        sql = '''
        SELECT c.id_meuble, c.nom_meuble, c.prix_meuble, lp.quantite
        FROM ligne_panier lp
        JOIN meuble c ON lp.meuble_id = c.id_meuble
        WHERE lp.utilisateur_id = %s
        '''
        mycursor.execute(sql, (id_client,))
        articles_panier = mycursor.fetchall()

        prix_total = sum(article['prix_meuble'] * article['quantite'] for article in articles_panier)

        return render_template('client/boutique/panier_article.html',
                               articles=articles,
                               articles_panier=articles_panier,
                               prix_total=prix_total,
                               items_filtre=types_article)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des articles : {str(e)}")
        flash(u'Une erreur est survenue lors du chargement des articles.', 'error')
        return redirect(url_for('show_accueil'))

@client_article.route('/client/article/details/<int:id>', methods=['GET'])
def client_article_details(id):
    mycursor = get_db().cursor()
    sql = '''
    SELECT c.*, t.libelle_type_meuble
    FROM meuble c
    LEFT JOIN type_meuble t ON c.type_meuble = t.id_type_meuble
    WHERE c.id_meuble = %s
    '''
    mycursor.execute(sql, (id,))
    article = mycursor.fetchone()

    sql = '''
    SELECT *
    FROM commentaire
    WHERE meuble_id = %s
    ORDER BY date_publication DESC
    '''
    mycursor.execute(sql, (id,))
    commentaires = mycursor.fetchall()

    return render_template('client/boutique/article_details.html', article=article, commentaires=commentaires)

@client_article.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    quantite = request.form.get('quantite', None)
    if id_article and quantite:
        sql = "SELECT stock FROM meuble WHERE id_meuble= %s"
        mycursor.execute(sql, (id_article,))
        stock = mycursor.fetchone()['stock']
        if stock >= int(quantite):
            sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
            mycursor.execute(sql, (id_client, id_article))
            result = mycursor.fetchone()
            if result:
                new_quantite = result['quantite'] + int(quantite)
                sql = "UPDATE ligne_panier SET quantite = %s WHERE utilisateur_id = %s AND meuble_id = %s"
                mycursor.execute(sql, (new_quantite, id_client, id_article))
            else:
                sql = "INSERT INTO ligne_panier (utilisateur_id, meuble_id, quantite) VALUES (%s, %s, %s)"
                mycursor.execute(sql, (id_client, id_article, quantite))
            get_db().commit()
            flash(u'Article ajouté au panier avec succès !', 'success')
        else:
            flash(u'Stock insuffisant !', 'danger')
    return redirect(url_for('client_article.client_article_show'))

@client_article.route('/client/panier/remove', methods=['POST'])
def client_panier_remove():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    if id_article:
        sql = "SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
        mycursor.execute(sql, (id_client, id_article))
        result = mycursor.fetchone()
        if result and result['quantite'] > 1:
            new_quantite = result['quantite'] - 1
            sql = "UPDATE ligne_panier SET quantite = %s WHERE utilisateur_id = %s AND meuble_id = %s"
            mycursor.execute(sql, (new_quantite, id_client, id_article))
        else:
            sql = "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
            mycursor.execute(sql, (id_client, id_article))
        get_db().commit()
        flash(u'Quantité mise à jour dans le panier', 'success')
    return redirect(url_for('client_article.client_article_show'))

@client_article.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    if id_article:
        sql = "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND meuble_id = %s"
        mycursor.execute(sql, (id_client, id_article))
        get_db().commit()
        flash(u'Article supprimé du panier avec succès !', 'success')
    return redirect(url_for('client_article.client_article_show'))

@client_article.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = "DELETE FROM ligne_panier WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    get_db().commit()
    flash(u'Panier vidé avec succès !', 'success')
    return redirect(url_for('client_article.client_article_show'))

@client_article.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    session['filter_word'] = request.form.get('filter_word', '')
    session['filter_types'] = request.form.getlist('filter_types')
    session['filter_prix_min'] = request.form.get('filter_prix_min', '')
    session['filter_prix_max'] = request.form.get('filter_prix_max', '')
    return redirect(url_for('client_article.client_article_show'))

@client_article.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_types', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    flash(u'Tous les filtres ont été supprimés.', 'info')
    return redirect(url_for('client_article.client_article_show'))

@client_article.route('/client/article/refresh', methods=['GET'])
def client_article_refresh():
    return client_article_show()

@client_article.route('/debug')
def debug_info():
    mycursor = get_db().cursor()
    try:
        mycursor.execute("SELECT * FROM meuble")
        meuble_data = mycursor.fetchall()
        mycursor.execute("SELECT * FROM type_meuble")
        type_meuble_data = mycursor.fetchall()
        return f"Données meuble : {str(meuble_data)}<br><br>Données type_meuble : {str(type_meuble_data)}"
    except Exception as e:
        return f"Erreur lors de la récupération des données : {str(e)}"



