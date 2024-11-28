#import
import streamlit as st
import pandas as pd
import requests
import json
import time

#chargement de la database imdb
def get_imdb_data():
    link="https://github.com/Wilderenfurie/Wild_Projet2/blob/61f589997a872074ac131880467b446da300473b/df_full.csv?raw=true"
    df_movie=pd.read_csv(link)
    df_movie=df_movie.astype('str').replace(r'\.0$', '', regex=True)
    return df_movie

with st.spinner('Chargement de la base de données'):
    df_movie=get_imdb_data()


#chargement de l'api TMDB
url ="https://api.themoviedb.org/3/"
key="?api_key=5b37793600df32594ef72adc9aa2bc75"
lang="&language=fr"

def appel_api(request):
    response=requests.get(url+request)
    result=response.json()
    return result



#construction de la page
st.title("Bienvenue sur les recommandations de votre cinéma")
st.header("powered by Dat'One")
