import streamlit as st
import pandas as pd
import requests
import json
import time

import urllib.parse

#chargement de la database imdb
def get_imdb_data():
    link="https://github.com/Wilderenfurie/Wild_Projet2/blob/61f589997a872074ac131880467b446da300473b/df_full.csv?raw=true"
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
st.header("Powered by Dat'Way")
df_movie

# Champs de recherche utilisateur
titre_film = st.text_input("Recherchez un film par titre:")

# Résultats de la recherche
if titre_film:
    with st.spinner("Recherche en cours, patientez svp..."):
        # Effectuer la recherche via l'API TMDB
        searche_resultats = search_movie(titre_film)

    # Si des résultats sont trouvés
    if searche_resultats.get("results"):
        films = searche_resultats["results"]
        
        # Affichage des premiers résultats trouvés
        for film in films[:5]:  # Limite à 5 films pour ne pas trop encombrer l'écran
            st.subheader(film["title"])
            
            # Affichage de l'affiche du film
            poster_url = f"https://image.tmdb.org/t/p/w500{film['poster_path']}" if film.get('poster_path') else None
            if poster_url:
                st.image(poster_url, width=200)
    else:
        st.write("Aucun film trouvé pour ce titre.")

