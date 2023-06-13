from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField,FloatField,SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from JoStreamIvoire.models import Utilisateur,Film


class RegisterForm(FlaskForm):
    def validate_nom_utilisateur(self, nom_utilisateur_to_check):
        nom_utilisateur = Utilisateur.query.filter_by(nom_utilisateur=nom_utilisateur_to_check.data).first()
        if nom_utilisateur:
            raise ValidationError('Nom utilisateur déjà existant !')

    def validate_mail(self, mail_address_to_check):
        mail = Utilisateur.query.filter_by(mail=mail_address_to_check.data).first()
        if mail:
            raise ValidationError('Adresse email déjà existante !')

    nom_utilisateur = StringField(label="Nom d'Utilisateur", validators=[Length(min=2, max=30), DataRequired()])
    mail = StringField(label='Adresse Mail:', validators=[Email(), DataRequired()])
    genre = SelectField(label='Genre:', choices=[('Homme', 'Homme'), ('Femme', 'Femme'),('Nonbinaire', 'Nonbinaire'),('NR', 'Je prefere ne pas repondre')],validators=[DataRequired()])
    ville = StringField(label='Ville:', validators=[DataRequired()])
    password1 = PasswordField(label='Mot de passe:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirmer:', validators=[EqualTo('password1'), DataRequired()])
    soumettre = SubmitField(label='Créer le compte')


class LoginForm(FlaskForm):
    nom_utilisateur = StringField(label="Nom d'Utilisateur", validators=[DataRequired()])
    mdp = PasswordField(label='Mot de passe:', validators=[DataRequired()])
    soumettre = SubmitField(label='Connexion')

    
class RetirerFilm(FlaskForm):
    soumettre = SubmitField(label='Dévoter')