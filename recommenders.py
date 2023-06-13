#Imports usuels
import pandas as pd

# Pour le pré processing
from unidecode import unidecode
import re
from nltk.stem import SnowballStemmer

# Pour la vectorisation
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import linear_kernel

#Importation depuis la base de données
import sqlite3


# Établir une connexion à la base de données
conn = sqlite3.connect('JoStreamIvoire/JoStreamIvoire.db')

# Créer un curseur pour exécuter des requêtes
cur = conn.cursor()

# Exécuter la requête pour récupérer tous les éléments de la table "films"
cur.execute("SELECT * FROM film")

# Récupérer les résultats de la requête dans une liste
results = cur.fetchall()
columns = [description[0] for description in cur.description]
# Fermer le curseur et la connexion à la base de données
cur.close()
conn.close()

# Créer un filmsframe à partir des résultats
films = pd.DataFrame(results, columns=columns)


#Statistiques de la base

C=films["vote_moyen"].mean()
m=films["nbre_votes"].quantile(0.5)
#print(f"--------mediane={m}")
v = films["nbre_votes"]
R = films["vote_moyen"]

films["score"]=((v*R)/(v+m) + (m*C)/(v+m))
print(films)
#1er tri
q_films = films[films["nbre_votes"]>=m].sort_values(by="score", ascending=False).drop_duplicates(subset=["titre"])

#q_films.sort_values(by="score", ascending=False, inplace=True)


#print(f"films triés {q_films}")
#Fonction de nettoyage des textes

def stem_cleaner(pandasSeries):
    # Définition de la liste de stop words considérés (celle de spacy + lettres)
    stopWords = pd.read_csv("../NLTK's list of english stopwords.csv",header=None).loc[:,0].tolist()
    # Création du stemmer
    stemmer = SnowballStemmer("english")

    # Création d'une fonction pour supprimer les stopWords
    def no_stop_word(string, stopWords):

        """
        Supprime les stop words d'un texte.

        Paramètres
        ----------

        string : chaine de caractère.

        stopWords : liste de mots à exclure. 
        """
        
        string =" ".join([mot for mot in string.lower().split(" ") if mot not in stopWords])
        return string

    # créer une fonction pour stemmiser les mots d'un text
    def stemmatise_text(text, stemmer):

        """
        Stemmatise un texte : Ramène les mots d'un texte à leur racine (peut créer des mots qui n'existe pas).

        Paramètres
        ----------

        text : Chaine de caractères.

        stemmer : Stemmer de NLTK.
        """
        
        ## code 
        string = " ".join([stemmer.stem(mot) for mot in text.lower().split(" ")])
        return string

    print("#### Nettoyage en cours ####") # Mettre des print vous permet de comprendre où votre code rencontre des problèmes en cas de bug
    
    # confirmation que chaque document est bien de type str
    pandasSeries = pandasSeries.apply(lambda x : str(x))
    
    ### COMMENCEZ A CODER ICI! remplacer les 'None' par votre code ###
    
    # Passage en minuscule
    print("... Passage en minuscule") 
    pandasSeries = pandasSeries.apply(lambda x : x.lower())
    
    # Suppression des accents
    print("... Suppression des accents") 
    pandasSeries = pandasSeries.apply(lambda x : unidecode(x))
    
    # Détection du champs année, c'est pour l'exmple, dans les articles de sports les années peuvent avoir leur importance
    # Encore une fois ça se test, tout comme toutes les transformations envisageables
    print("... Détection du champs année") 
    pandasSeries = pandasSeries.apply(lambda x : re.sub(r'[0-9]{4}', 'annee', x))
    
    # Suppression des caractères spéciaux et numériques
    print("... Suppression des caractères spéciaux et numériques") 
    pandasSeries = pandasSeries.apply(lambda x :re.sub(r"[^a-z]+", ' ', x))
    
    # Suppression des stop words
    print("... Suppression des stop words") 
    pandasSeries = pandasSeries.apply(lambda x : no_stop_word(x, stopWords))
    
    # Stemmatisation
    print("... Stemmatisation")
    pandasSeries = pandasSeries.apply(lambda x : stemmatise_text(x, stemmer))
    
    print("#### Nettoyage OK! ####")

    return pandasSeries




#Réorganisation des données
description=q_films
#print(description)
description['description_stem'] = stem_cleaner(description['description'])
description.reset_index(drop=True,inplace=True)

#print(description)

# Calcul de la matrice de similarité cosinus
tfidf = TfidfVectorizer(ngram_range=(1, 3)) 
tfidf.fit(description.loc[:,('description_stem')].values.astype('U')) # Les parenthèses permettent d'extraire la colonne sous forme de série pandas. Ne rien mettre passait aussi mais bof…
description_tfidf = tfidf.transform(description['description_stem'].values.astype('U')).toarray()
cos_sim_descriptions=linear_kernel(description_tfidf)


#Fonction pour faire les recommandations sur la base d'un titre
def liste_recommandations(titre:str,description=description)->list:
    def reverse_map(titre:str)->str:
        return (description.index[description["titre"]==titre][0])
    
    cos_sim_titre=pd.Series(cos_sim_descriptions[reverse_map(titre),:])
    top_cos_sims=cos_sim_titre.sort_values(ascending=False).head(5)[1:]
    top_indexes=top_cos_sims.index.tolist()
    liste=description.loc[top_indexes,"titre"].tolist()
    return liste
#print(f'recommandations:{liste_recommandations(description.loc[1,"titre"])}')
