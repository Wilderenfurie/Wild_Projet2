import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import requests
import json
import time
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import urllib.parse


# module nécessaire

import random



#chargement de la database imdb et mise en cache pour la performance
@st.cache_data
def get_imdb_data():
    link="https://github.com/Wilderenfurie/Wild_Projet2/blob/6976f00a59035d04ced3d71278f8904abb45fcdf/df_full.csv?raw=true"
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
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1YjM3NzkzNjAwZGYzMjU5NGVmNzJhZGM5YWEyYmM3NSIsIm5iZiI6MTczMjE5NzIxNC44MTMsInN1YiI6IjY3M2YzYjVlYWRlOTMxMGYzZmRmYTMxOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.NtriKj7asDAlbg0_at7JcrkW0fwDQnDr99ilDRLrtx4"
}

def appel_api(request):
    response = requests.get(url + request,headers=headers)
    result = response.json()
    return result


def accueil():
    st.write("Bienvenue sur cette application web géniale. Elle vous permet de chercher un film que vous aimez ou qui vous intrigue et de recevoir nos recommendations pour des films similaires")

def recherche_film_par_acteur(actor):
        
        # création de la liste de films de l'acteur choisi

        movies_by_actor=[]

        for idx, row in df_movie.iterrows():
            if  actor in row['primaryName'] :
                movies_by_actor.append(idx)

        # affichage des résultats

        col_image,col_resume=st.columns(2,vertical_alignment='center')
        col_recommandations1,col_recommandations2=st.columns([0.999,0.001],vertical_alignment='top')
        col_film1,  col_film2,  col_film3 = st.columns(3,vertical_alignment='center')
        columns = [ col_film1,  col_film2,  col_film3] 

        cpt=0
        for x, id_movie in enumerate(movies_by_actor):
            current_col = columns[cpt % 3]
            with current_col:
                st.text("")
                st.text("")
                st.text("")
                st.text("")
                st.write(df_movie["originalTitle"].iloc[id_movie])
                poster_url = f"https://image.tmdb.org/t/p/w500{df_movie['poster'].iloc[id_movie]}"
                if poster_url:
                    st.image(poster_url, width=200)
            cpt+=1

def page():
    if selection == "Accueil":
        accueil()

    elif selection =="Rechercher par acteur":
       
       # création de la liste d'acteurs
        df_movie['primaryName'] = df_movie['primaryName'].apply(lambda x: x.replace('[', '').replace(']', '').replace("'","").replace('"',"").strip().split(','))
        all_actors = sorted(df_movie['primaryName'].drop_duplicates().explode().unique())
  
        # input utilisateur pour choisir un acteur
        actor = st.selectbox("Choisissez un acteur : ", all_actors, index =all_actors.index(' Pierre Niney'))

        recherche_film_par_acteur(actor)


with st.sidebar:
        selection = option_menu(
                    menu_title=None,
                    options = ["Accueil","Rechercher par titre","Rechercher par acteur"]
        )


# Construction de la page Streamlit
st.title("Bienvenue sur les recommandations de votre cinéma")
st.text("Powered by Dat'One")
st.text("")
st.text("")
st.text("")
st.text("")

page()

                
                   
                   
