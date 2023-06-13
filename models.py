from JoStreamIvoire import db, login_manager
from JoStreamIvoire import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Utilisateur.query.get(int(user_id))

class Utilisateur(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    nom_utilisateur = db.Column(db.String(length=30), nullable=False, unique=True)
    mail = db.Column(db.String(length=50), nullable=False, unique=True)
    gender = db.Column(db.String(length=50), nullable=False, unique=True)
    ville = db.Column(db.String(length=50), nullable=False, unique=True)
    mdp_crypte = db.Column(db.String(length=60), nullable=False)
    nbre_votes_dispo = db.Column(db.Integer(), nullable=False, default=10)
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.mdp_crypte = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.mdp_crypte, attempted_password)

    def peut_voter(self):
        return self.nbre_votes_dispo > 0

    def peut_retirer(self):
        return self.nbre_votes_dispo < 10

class Film(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    titre = db.Column(db.String(), nullable=False, unique=False)
    tagline = db.Column(db.String(), nullable=False)
    genres=db.Column(db.String(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    duree=db.Column(db.Float, nullable=False)
    nbre_votes=db.Column(db.Integer(), nullable=False,default=0)
    vote_moyen=db.Column(db.Float(), nullable=False,default=0)
    last_vote=db.Column(db.Float(), nullable=False,default=10)
    def __repr__(self):
        return f'Film {self.titre}'
    
    def vote(self, user,vote):
        self.nbre_votes+=1
        self.vote_moyen += vote/ self.nbre_votes
        user.nbre_votes_dispo-=1
        self.last_vote=vote
        db.session.commit()
 
        
    def retirer(self, user):
        self.nbre_votes-=1
        self.vote_moyen -= self.last_vote/ self.nbre_votes
        user.nbre_votes_dispo+=1
        db.session.commit()