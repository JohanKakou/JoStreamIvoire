from JoStreamIvoire import app
from JoStreamIvoire.recommenders import liste_recommandations,description
from flask import render_template, redirect, url_for, flash, request
from JoStreamIvoire.models import Film, Utilisateur
from JoStreamIvoire.forms import RegisterForm, LoginForm
from JoStreamIvoire import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def accueil():
    return render_template('home.html')


@app.route('/description_film/', methods=['GET', 'POST'])
def noter_film(film):
    objet_film_choisi = Film.query.filter_by(id=film["id"]).first()
    if request.method == 'POST':
        note = request.form.get('note')  # Récupérer la note soumise dans le formulaire
        if current_user.peut_voter(objet_film_choisi):
            objet_film_choisi.vote(current_user,note)
            flash(f"Félicitation pour ce choix avisé !: {objet_film_choisi.titre} reçoit la note de {note} sur 10 !!!", category='success')
        else:
            flash(f"Désolé, vous ne pouvez plus voter {objet_film_choisi.titre} car vous n'avez plus de points de vote !!!", category='danger')
        # Logique pour enregistrer la note pour le film avec l'ID spécifié
        return redirect(url_for('noter_film',film=film))

    # Si la méthode est GET, afficher le formulaire de notation du film
    if request.method=='GET':
        return render_template('NoteFilm.html', film=film)

@app.route('/JoStreamIvoire', methods=['GET'])
@login_required
def JoStreamIvoire():
    films = description[["id","nbre_votes","description","vote_moyen","titre"]][:10]
    voted_films = description[description["last_vote"]!=10]
    
    return render_template('JoStreamIvoire.html', films=films,voted_films=voted_films)

@app.route('/register', methods=['GET', 'POST'])
def register_page():    
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = Utilisateur(nom_utilisateur=form.nom_utilisateur.data,
                                     mail=form.mail.data,
                                     password=form.password1.data,
                                     gender=form.genre.data,
                                     ville=form.ville.data
                                    )
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Compte créé avec succès pour vous, {user_to_create.nom_utilisateur}", category='success')
        return redirect(url_for('JoStreamIvoire'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'Il s\'est produit une erreur pendant la création de l\'utilisateur: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Utilisateur.query.filter_by(nom_utilisateur=form.nom_utilisateur.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.mdp.data
        ):
            login_user(attempted_user)
            flash(f'Vous êtes connecté en tant que {attempted_user.nom_utilisateur}', category='success')
            return redirect(url_for('JoStreamIvoire'))
        else:
            flash('Nom d\'utilisateur ou mot de passe ne correspondent pas! Veuillez réessayer', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("Vous avez été déconnecté !", category='info')
    return redirect(url_for("accueil"))









