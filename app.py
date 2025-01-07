import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import requests
import json
import time
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import urllib.parse
from deep_translator import GoogleTranslator

#chargement de la database imdb et mise en cache pour la performance
@st.cache_data
def get_imdb_data():
    link="https://github.com/Wilderenfurie/Wild_Projet2/blob/6976f00a59035d04ced3d71278f8904abb45fcdf/df_full.csv?raw=true"
    df_movie=pd.read_csv(link)
    df_movie=df_movie.astype('str').replace(r'\.0$', '', regex=True)
    df_movie=df_movie.drop_duplicates()
    df_movie=df_movie.dropna()
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

#fonction qui retourne le premier genre du film
def get_top_1_genres(genres):
    genres=genres.replace("]","")
    genres=genres.replace("[","")
    genres=genres.replace("'","")
    # Splitter les genres, les trier, et prendre les deux premiers
    genres = genres.split(",")
    return ",".join(genres[:1])




#traduction pour les résumés de film
translator = GoogleTranslator(source='en', target='fr')

def accueil():
    st.write("Bienvenue sur cette application web géniale. elle vous permet de chercher un film que vous aimez ou qui vous intrigue et de recevoir nos recommendations pour des films similiraires")
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
            
            # Creation du detail et appel de la fonction
            detail_titre=df_movie["originalTitle"].iloc[index]
            detail_resume=df_movie["resume"].iloc[index]
            detail_genre=df_movie["genre"].iloc[index]
            detail_pays=df_movie['Pays_prod'].iloc[index]
            detail_poster=poster_url
            detail_duree=df_movie["duree"].iloc[index]
            detail_note=df_movie["moyenne"].iloc[index]
            detail_acteurs=df_movie['primaryName'].iloc[index]
            st.button("Détails",type="secondary",key=cpt,on_click=detail,args=(detail_titre,detail_resume,detail_genre,detail_pays,detail_poster,detail_duree,detail_note,detail_acteurs))
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
                        resume=df_movie["resume"].iloc[index]
                        resume_fr = translator.translate(resume)
                        st.write(resume_fr)
                        
                        # Creation du detail et appel de la fonction
                        detail_titre=df_movie["originalTitle"].iloc[index]
                        detail_resume=df_movie["resume"].iloc[index]
                        detail_genre=df_movie["genre"].iloc[index]
                        detail_pays=df_movie['Pays_prod'].iloc[index]
                        detail_poster=poster_url
                        detail_duree=df_movie["duree"].iloc[index]
                        detail_note=df_movie["moyenne"].iloc[index]
                        detail_acteurs=df_movie['primaryName'].iloc[index]
                        st.button("Détails",type="secondary",key=cpt,on_click=detail,args=(detail_titre,detail_resume,detail_genre,detail_pays,detail_poster,detail_duree,detail_note,detail_acteurs))
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
                    
                        # Creation du detail et appel de la fonction
                        detail_titre=df_movie["originalTitle"].iloc[index]
                        detail_resume=df_movie["resume"].iloc[index]
                        detail_genre=df_movie["genre"].iloc[index]
                        detail_pays=df_movie['Pays_prod'].iloc[index]
                        detail_poster=poster_url
                        detail_duree=df_movie["duree"].iloc[index]
                        detail_note=df_movie["moyenne"].iloc[index]
                        detail_acteurs=df_movie['primaryName'].iloc[index]
                        st.button("Détails",type="secondary",key=cpt,on_click=detail,args=(detail_titre,detail_resume,detail_genre,detail_pays,detail_poster,detail_duree,detail_note,detail_acteurs))
                cpt+=1

# Fonction details qui affiche un maximum d'info a l'utilisateur 
@st.dialog("Détails")
def detail(detail_titre,detail_resume,detail_genre,detail_pays,detail_poster,detail_duree,detail_note,detail_acteurs):
    st.subheader(detail_titre)
    st.write("Genre : "+translator.translate(detail_genre))
    st.write(detail_pays)
    st.write("Durée : "+detail_duree + " min")
    st.write("Note : "+detail_note)
    st.write("Casting : "+detail_acteurs)
    st.image(detail_poster, width=200)
    detail_resume = translator.translate(detail_resume)
    st.write(detail_resume)
 
    

def recherche_film_par_acteur(acteur,duree_deb,duree_fin,pays,note_deb,note_fin,genre,annee_deb,annee_fin):
    # Boucle sur l'acteur et mise en place des filtres et de la mise en page si acteur trouvé
    result=0
    for name,job in zip(df_movie['primaryName'],df_movie['primaryProfession']):
        if  acteur in name and ('actor' in job or 'actress' in job):
            index=df_movie[df_movie['primaryName']==name].index
            if ((duree_deb<=int(df_movie["duree"].iloc[index[0]]))  &  (int(df_movie["duree"].iloc[index[0]])<=duree_fin)):
                if ((note_deb<=float(df_movie["moyenne"].iloc[index[0]]))  &  (float(df_movie["moyenne"].iloc[index[0]])<=note_fin)):
                    if ((annee_deb<=int(df_movie["annee"].iloc[index[0]])) & (int(df_movie["annee"].iloc[index[0]]) <=annee_fin)):
                        if any(p in df_movie['Pays_prod'].iloc[index[0]] for p in pays) or not pays:
                            if any(g in df_movie['genre'].iloc[index[0]] for g in genre) or not genre:

                                col1,col4=st.columns(2,vertical_alignment="center")
                                col2,col3 = st.columns(2,vertical_alignment="center")
                            
                                with col1:
                                    st.write(" ")
                                    st.write(" ")
                                    st.write(" ")
                                    st.subheader(df_movie["originalTitle"].iloc[index[0]])
                                with col2:
                                    poster_url = f"https://image.tmdb.org/t/p/w500{df_movie['poster'].iloc[index[0]]}"
                                    if poster_url:
                                        st.image(poster_url, width=200)
                                with col3:
                                    resume=df_movie["resume"].iloc[index[0]]

                                    resume = translator.translate(resume)
                                    st.write(resume)

                                # Creation du detail et appel de la fonction
                                detail_titre=df_movie["originalTitle"].iloc[index[0]]
                                detail_resume=df_movie["resume"].iloc[index[0]]
                                detail_genre=df_movie["genre"].iloc[index[0]]
                                detail_pays=df_movie['Pays_prod'].iloc[index[0]]
                                detail_poster=poster_url
                                detail_duree=df_movie["duree"].iloc[index[0]]
                                detail_note=df_movie["moyenne"].iloc[index[0]]
                                detail_acteurs=df_movie['primaryName'].iloc[index[0]]
                                st.button("Détails",type="secondary",key=result,on_click=detail,args=(detail_titre,detail_resume,detail_genre,detail_pays,detail_poster,detail_duree,detail_note,detail_acteurs))
                                
                                st.write(" ")
                                st.write(" ")
                                st.write(" ")
                                # on indique que l'on a un resultat
                                result+=1

    # Si aucun acteur trouvé on affiche un message d'erreur
    if result==0:
        st.write("Nous ne connaissons pas cet acteur ou filtres incorrect")



def page():
    if selection == "Accueil":
        accueil()

    elif selection == "Rechercher par titre":
        # Champs de recherche du titre
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

    elif selection =="Rechercher par acteur":
        # Champs de recherche de l'acteur et création des filtres
        col_filtre1,col_filtre2,col_filtre3=st.columns(3,vertical_alignment="center")
        col_filtre4,col_filtre5=st.columns(2,vertical_alignment="center")
        with col_filtre1:
            runtime=df_movie["duree"].astype('int').drop_duplicates().sort_values().to_list()
            duree_deb,duree_fin=st.select_slider("Durée",runtime,[min(runtime),max(runtime)])
        with col_filtre2:
            pays_prod=df_movie["Pays_prod"].apply(get_top_1_genres).drop_duplicates().sort_values().to_list()
            pays=st.multiselect("Pays",pays_prod)
        with col_filtre3:
            score=df_movie["moyenne"].astype('float').drop_duplicates().sort_values().to_list()
            note_deb,note_fin=st.select_slider("Note",score,[min(score),max(score)])

        with col_filtre4:
            genra=df_movie["genre"].apply(get_top_1_genres).drop_duplicates().sort_values().to_list()
            genra.insert(0,"")
            genra.pop()
            genre=st.multiselect("Genre",genra)
            
        with col_filtre5:
            annee=df_movie["annee"].astype('int').drop_duplicates().sort_values().to_list()
            annee_deb,annee_fin=st.select_slider("Année",annee,value=[min(annee),max(annee)])

        acteur = st.text_input("Recherchez un Acteur / Actrice")

        # Resultat de la recherche
        if acteur!="":
            recherche_film_par_acteur(acteur,duree_deb,duree_fin,pays,note_deb,note_fin,genre,annee_deb,annee_fin)


# On ajoute la sidebar et on lui affecte nos pages
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

# On appelle la fonction page qui contient les autres fonctions 
page()

# Ajout d'elements de styles               
st.markdown(
    """
    <style>
    button {
        cursor: pointer;
        transition: all .2s ease-in-out;
    }
    button:hover {
        transform: scale(1.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)          
                   
