import streamlit as st
import pandas as pd
import requests
import json
import time
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

import urllib.parse

#chargement de la database imdb
def get_imdb_data():
    link="https://github.com/Wilderenfurie/Wild_Projet2/blob/c7bb8b56c944b9258a153d7195ceab13921365b2/df_full.csv?raw=true"
    df_movie=pd.read_csv(link)
    df_movie=df_movie.astype('str').replace(r'\.0$', '', regex=True)
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

# Recherche d'un film sur TMDB par titre
def search_movie(title):
    # Encodage de l'input pour éviter les problèmes avec les espaces ou caractères spéciaux
    encoded_title = urllib.parse.quote(title)
    endpoint = f"search/movie?api_key={key}&query={encoded_title}{lang}"
    result = appel_api(endpoint)
    return result

# Construction de la page Streamlit
st.title("Bienvenue sur les recommandations de votre cinéma")
st.header("Powered by Dat'One")

# Champs de recherche utilisateur
titre_film = st.selectbox("Recherchez un film par titre:",df_movie["originalTitle"])

# Résultats de la recherche
if titre_film:
    with st.spinner("Recherche en cours, patientez svp..."):
        for title in df_movie["originalTitle"]:
            if titre_film==title:
                df_knn=df_movie[["originalTitle","id_imdb","id","genre","annee","moyenne","Pays_prod","duree"]]
                df_knn=df_knn.dropna()
                df_knn["genre_fact"]=df_knn["genre"].factorize()[0]
                df_knn["Pays_prod_fact"]=df_knn["Pays_prod"].factorize()[0]
                X_scaled=StandardScaler().fit_transform(df_knn[["genre_fact","annee","moyenne","Pays_prod_fact","duree"]])
                model=NearestNeighbors(n_neighbors=4)
                model=model.fit(X_scaled)

                film_index=df_knn[df_knn["originalTitle"]==title].index[0]
                distances, indices=model.kneighbors(X_scaled[film_index].reshape(1,-1))
                for distance, index in zip(distances[0][0:], indices[0][0:]):
                    st.write(df_movie["originalTitle"].iloc[index])
                    poster_url = f"https://image.tmdb.org/t/p/w500{df_movie['poster'].iloc[index]}"
                    if poster_url:
                        st.image(poster_url, width=200)
                    st.write(df_knn.iloc[index])
                   
