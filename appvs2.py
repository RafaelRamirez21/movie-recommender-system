import streamlit as st
import pickle
import pandas as pd
import requests
import os
import gdown

# === CONFIG ===
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]  # Usar desde secrets en Streamlit Cloud

# === ARCHIVOS REMOTOS ===
MOVIES_DICT_ID = "18VXa4-b6KLt3JzosaEBQi1K_cvkMc2t7"
SIMILARITY_ID = "1CNqe6rTcgJcnsYNi4GOdJKx0TSthw1PL"


MOVIES_DICT_FILE = "movies_dict.pkl"
SIMILARITY_FILE = "similarity.pkl"

def descargar_archivo(gdrive_id, local_filename):
    if not os.path.exists(local_filename):
        url = f"https://drive.google.com/uc?id={gdrive_id}"
        gdown.download(url, local_filename, quiet=False)

# === DESCARGA DE ARCHIVOS ===
descargar_archivo(MOVIES_DICT_ID, MOVIES_DICT_FILE)
descargar_archivo(SIMILARITY_ID, SIMILARITY_FILE)

# === CARGA DE DATOS ===
movies_dict = pickle.load(open(MOVIES_DICT_FILE, 'rb'))
similarity = pickle.load(open(SIMILARITY_FILE, 'rb'))
movies = pd.DataFrame(movies_dict)

# === FUNCIONES ===
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get("poster_path")
    return f"https://image.tmdb.org/t/p/w500{poster_path}"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# === UI ===
st.title('🎬 Movie Recommender System')
selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
