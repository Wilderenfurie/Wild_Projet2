import streamlit as st
import pandas as pd
import requests
import json
import time
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import urllib.parse

#chargement de la database imdb et mise en cache pour la performance
@st.cache_data
def get_imdb_data():
    link="https://github.com/Wilderenfurie/Wild_Projet2/blob/6e3e46ee8a87b156ed88f0d9988f1b0b3c910283/df_full.csv?raw=true"
    df_movie=pd.read_csv(link)
    df_movie=df_movie.astype('str').replace(r'\.0$', '', regex=True)
    df_movie=df_movie.drop_duplicates()
    return df_movie

with st.spinner('Chargement de la base de données'):
    df_movie=get_imdb_data()


# Chargement de l'API TMDB
url = "https://api.themoviedb.org/3/"
key = "5b37793600df32594ef72adc9aa2bc75"
lang = "&language=fr"

def appel_api(request):
    response = requests.get(url + request)
    result = response.json()
    return result


# Construction de la page Streamlit
st.title("Bienvenue sur les recommandations de votre cinéma")
st.text("Powered by Dat'One")
st.text("")
st.text("")
st.text("")
st.text("")

# Champs de recherche utilisateur
options_dict = {f"{row['originalTitle']}  [{row['annee']}]": idx for idx, row in df_movie.iterrows()}
options = [""] + list(options_dict.keys())
titre_film = st.selectbox("Recherchez un film par titre :", options)
st.text("")
st.text("")
st.text("")
st.text("")

# Résultats de la recherche
if titre_film!="":
    with st.spinner("Recherche en cours, patientez svp..."):

        #df provisoire pour le knn et suppressiond des nan
        df_knn=df_movie[["originalTitle","id_imdb","id","genre","annee","moyenne","Pays_prod","duree"]]
        df_knn=df_knn.dropna()

        #création des dummies et normalisations des données
        df_pays=pd.get_dummies(df_knn["Pays_prod"],prefix="Pays_prod")
        df_dummy = pd.get_dummies(df_knn["genre"], prefix="genre")
        df_X=pd.DataFrame(StandardScaler().fit_transform(df_knn[["annee","moyenne","duree"]]))

        #concaténations des données normalisée et des dummies afin d'avoir un X_scaled complet et normalisées
        X_scaled = pd.concat([df_X, df_dummy,df_pays], axis=1)
        X_scaled.columns=X_scaled.columns.astype('str')

        #création du knn et entrainement du modèle sur notre X_scaled
        model=NearestNeighbors(n_neighbors=4)
        model=model.fit(X_scaled)

        #on va chercher l'index du film choisi, la target
        film_index = options_dict[titre_film]


        #on applique le kneighbors sur le film choisi présent dans le X_scaled
        distances, indices=model.kneighbors(X_scaled.iloc[film_index].values.reshape(1, -1))
        
        #création de colonnes pour l'affichage des films 
        col_image,col_resume=st.columns(2,vertical_alignment='center')
        col_recommandations1,col_recommandations2=st.columns([0.999,0.001],vertical_alignment='top')
        col_film1,  col_film2,  col_film3 = st.columns(3,vertical_alignment='center')
        columns = [ col_film1,  col_film2,  col_film3] 

        #creation d'un compteur
        cpt=0

        #on boucle sur chaque films présent dans les resultats du knn pour l'afficher dans les colonnes respectives
        for distance, index in zip(distances[0][0:], indices[0][0:]):
            if cpt==0:
                with col_image:
                    st.subheader(df_movie["originalTitle"].iloc[index])
                    poster_url = f"https://image.tmdb.org/t/p/w500{df_movie['poster'].iloc[index]}"
                    if poster_url:
                        st.image(poster_url, width=200)
                with col_resume:
                    st.write(df_movie["resume"].iloc[index])

                with col_recommandations1:
                    st.divider()
                    st.subheader("On vous recommande aussi :")
                with col_recommandations2:
                    st.divider()
            else:
                current_col = columns[cpt % 3]
                with current_col:
                    st.text("")
                    st.text("")
                    st.text("")
                    st.text("")
                    st.write(df_movie["originalTitle"].iloc[index])
                    poster_url = f"https://image.tmdb.org/t/p/w500{df_movie['poster'].iloc[index]}"
                    if poster_url:
                        st.image(poster_url, width=200)
            cpt+=1
            
                
                   
                   
