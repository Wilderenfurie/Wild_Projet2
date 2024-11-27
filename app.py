#import
import streamlit as st
import pandas as pd
import requests
import json
import time



#chargement de la database imdb
def get_imdb_data():
    link="https://drive.google.com/file/d/12-m1RbdfoQz1SgdQOI8rmuZFh16HjdCg/view?usp=sharing"
    link='https://drive.google.com/uc?export=download&id=' + link.split('/')[-2] +'&confirm=t'
    df_movie=pd.read_csv(link)
    #df_movie=df_movie.astype('str').replace(r'\.0$', '', regex=True)
    return df_movie

with st.spinner('Chargement de la base de données'):
    df_movie=get_imdb_data()
    id_list_imdb=df_movie.tconst.to_list()


#chargement de l'api TMDB
url ="https://api.themoviedb.org/3/"
key="?api_key=5b37793600df32594ef72adc9aa2bc75"
lang="&language=fr"

def appel_api(request):
    response=requests.get(url+request)
    result=response.json()
    return result


#récupération des id tmdb en fonction de nos id imdb
#def find_movie_by_id():
#    list_df=[]
#   for id in id_list_imdb:
#         result=appel_api("find/"+id+""+key+"&external_source=imdb_id"+lang)
#         df_movie_tmdb = pd.json_normalize(result)
#        df_movie_tmdb['tconst'] = id
#         list_df.append(df_movie_tmdb)
#    return pd.concat(list_df)
#df_id_tmdb=find_movie_by_id()




#construction de la page
st.title("Bienvenue sur les recommandations de votre cinéma")
st.header("powered by Dat'Way ")
st.write(df_movie)
st.write(id_list_imdb)



