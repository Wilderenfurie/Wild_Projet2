import streamlit as st
from streamlit_option_menu import option_menu
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

#fonction qui retourne les deux premier genres du film
def get_top_2_genres(genres):
    genres=genres.replace("]","")
    genres=genres.replace("[","")
    genres=genres.replace("'","")
    # Splitter les genres, les trier, et prendre les deux premiers
    genres = genres.split(",")
    return ",".join(genres[:2])

def accueil():
    st.write("Bienvenu sur cette application web géniale. elle vous permet de chercher un film que vous aimez ou qui vous intrigue et de recevoir nos recommensations pour des films similiraires")
    st.divider()
    st.subheader("Voici nos 10 films les plus populaires:")
    df_top10=df_movie.sort_values(["moyenne",'nb_votes'],ascending=False)
    df_top10=df_top10[df_top10['nb_votes'].astype('int')>int(1000000)]
    df_top10=df_top10.head(10)

    cola,col1,colb=st.columns(3,vertical_alignment="center")
    col2,col3,col4=st.columns(3,vertical_alignment="center")
    col5,col6,col7=st.columns(3,vertical_alignment="center")
    col8,col9,col10=st.columns(3,vertical_alignment="center")
    columns = [col1,col2,col3,col4,col5,col6,col7,col8,col9,col10] 
    cpt=0

    for index,row in df_top10.iterrows():
        current_col = columns[cpt % 10]
        with current_col:
            st.text("")
            st.text("")
            st.text("")
            st.text("")
            st.write(row["originalTitle"])
            poster_url = f"https://image.tmdb.org/t/p/w500{row['poster']}"
            if poster_url:
                st.image(poster_url, width=200)
        cpt+=1


def recherche_film_par_titre(options_dict,titre_film):
        with st.spinner("Recherche en cours, patientez svp..."):

            #df provisoire pour le knn et suppressiond des nan
            df_knn=df_movie[["originalTitle","id_imdb","id","genre","annee","moyenne","Pays_prod","duree"]]
            df_knn["genre"] = df_knn["genre"].apply(get_top_2_genres)
            df_knn=df_knn.dropna()

            #création des dummies
            df_pays=pd.get_dummies(df_knn["Pays_prod"],prefix="Pays_prod")
            df_genre = pd.get_dummies(df_knn["genre"], prefix="genre")
            df_X=df_knn[["annee","moyenne","duree"]]

            #concaténations des données 
            X_scaled = pd.concat([df_X,df_genre,df_pays], axis=1)
            
            #normalisation et des données afin d'avoir un X_scaled complet et normalisées
            X_scaled=pd.DataFrame(StandardScaler().fit_transform(X_scaled))
            X_scaled.columns=X_scaled.columns.astype('str')
            
            #création du knn et entrainement du modèle sur notre X_scaled
            model=NearestNeighbors(n_neighbors=4,metric='manhattan')
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


def page():
    if selection == "Accueil":
        accueil()
    elif selection == "Rechercher un film":
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
            recherche_film_par_titre(options_dict,titre_film)


with st.sidebar:
        selection = option_menu(
                    menu_title=None,
                    options = ["Accueil", "Rechercher un film"]
        )


# Construction de la page Streamlit
st.title("Bienvenue sur les recommandations de votre cinéma")
st.text("Powered by Dat'One")
st.text("")
st.text("")
st.text("")
st.text("")

page()

                
                   
                   
