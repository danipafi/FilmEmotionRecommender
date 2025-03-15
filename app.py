import pandas as pd
import dask.dataframe as dd
import os
import re
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import ast
import base64

# Set page configuration to "wide"
st.set_page_config(layout="wide")

# Function to convert a file to base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load header image as base64
header_image_path = "/Users/danielebelmiro/Downloads/Mr_ Observer - Barancan Dağıstan.jpeg"
header_image_base64 = get_base64_of_bin_file(header_image_path)

# CSS for cards, header, sidebar, titles and background
st.markdown("""
<style>
/* Main title with text stroke (pink) */
.title {
    font-size: 53px;
    text-align: left; 
    color: #FF69B4;
    font-family: 'Arial', sans-serif;
    margin-bottom: 10px;
    -webkit-text-stroke: 1px black;
}

/* Subtitle */
.subtitle {
    font-size: 18px;
    text-align: left;
    color: #333;
    font-family: 'Arial', sans-serif;
    margin-bottom: 30px;
}

/* Header container */
.header-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-width: 800px;
    max-width: 1200px;
    margin: auto;
    margin-bottom: 20px;
}

/* Card style with light beige background */
.card {
    background-color: #FFF8E7;  /* Light beige */
    padding: 15px;
    margin: 10px 0;
    border-radius: 8px;
    border: 2px solid #ccc;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-title {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    text-align: left;
}

/* Section headings (lilac for section headings) */
.section-heading {
    font-size: 32px;
    font-weight: bold;
    color: #C8A2C8;
    -webkit-text-stroke: 1px black;
    margin-bottom: 20px;
    text-align: left;
}

/* Sidebar adjustments */
.css-1d391kg { 
    max-width: 300px;
}
.css-1d391kg > div { 
    max-width: 300px;
}
</style>
""", unsafe_allow_html=True)

def normalize_name(name):
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    return name.lower().strip()

def generate_rotten_tomatoes_url(movie_id):
    return f"https://www.rottentomatoes.com/m/{movie_id}"

def get_movie_poster_url(movie_id):
    url = f"https://www.rottentomatoes.com/m/{movie_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tag = soup.find('meta', property="og:image")
    if meta_tag and meta_tag.get('content'):
        return meta_tag['content']
    poster_img = soup.find('img', {'class': 'posterImage'})
    if poster_img and 'src' in poster_img.attrs:
        return poster_img['src']
    return None

@st.cache_data
def load_data():
    reviews = pd.read_csv('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/reviews_emotions.csv')
    movies = pd.read_csv('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/movies_final.csv')
    movies['genre'] = movies['genre'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    movies['emotions'] = movies['emotions'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df_final_clean = pd.read_csv('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/df_final_clean.csv')
    return movies, reviews, df_final_clean

def render_movie_card(movie, poster_url, is_favorite=False):
    """
    Renders a card with the movie information.
    If is_favorite is True, uses a larger poster and omits the similarity score.
    The movie title is displayed prominently (aligned to the left).
    """
    poster_width = 240
    similarity_line = "" if is_favorite else f"<p><strong>🔗 Similarity Score:</strong> {movie.get('score', 0):.5f}</p>"
    if isinstance(movie['emotions'], (list, tuple)):
        emotional_profile_str = ", ".join([f"{mood}: {percentage:.1f}%" for mood, percentage in movie['emotions']])
    else:
        emotional_profile_str = movie['emotions']
    card_html = f"""
    <div class="card">
      <div class="card-title">🎬 {movie['title']}</div>
      <div style="display: flex; align-items: center;">
        <div style="flex: 1;">
          <img src="{poster_url}" width="{poster_width}" style="border-radius: 5px;">
        </div>
        <div style="flex: 2; padding-left: 15px;">
          <p><strong>🎥 Director:</strong> {movie['director']}</p>
          <p><strong>🌍 Language:</strong> {movie['originalLanguage']}</p>
          <p><strong>⏳ Duration:</strong> {movie['runtimeMinutes']} min</p>
          <p><strong>🎭 Genre:</strong> {", ".join(movie['genre']) if isinstance(movie['genre'], (list, tuple)) else movie['genre']}</p>
          <p><strong>📅 Year:</strong> {movie['release_year']}</p>
          <p><strong>🍅 Tomatometer:</strong> {movie['tomatoMeter']}%</p>
          <p><strong>🎟️ Audience Score:</strong> {movie['audienceScore']}%</p>
          {similarity_line}
          <p><strong>❤️ Emotional Profile:</strong> {emotional_profile_str}</p>
          <p><a href="{generate_rotten_tomatoes_url(movie['id'])}" target="_blank">🔗 Link to Rotten Tomatoes</a></p>
        </div>
      </div>
    </div>
    """
    card_html = " ".join(card_html.splitlines())
    st.markdown(card_html, unsafe_allow_html=True)

def recommend_similar_movies(df_final_clean, movies, reviews, favorite_movie, top_n=5):
    movies = movies.copy()
    favorite_movie_normalized = normalize_name(favorite_movie)
    matching_movies = movies[movies['title_normalized'] == favorite_movie_normalized]
    if matching_movies.empty:
        st.error(f"❌ The movie '{favorite_movie}' was not found. Please check the name and try again.")
        return None
    favorite_movie_id = matching_movies.iloc[0]['id']
    favorite_movie_title = matching_movies.iloc[0]['title']
    st.success(f"✅ Movie found: {favorite_movie_title} (ID: {favorite_movie_id})")
    fav_movie = matching_movies.iloc[0].to_dict()
    fav_poster_url = get_movie_poster_url(favorite_movie_id)
    st.markdown('<div class="section-heading">Favorite Movie</div>', unsafe_allow_html=True)
    render_movie_card(fav_movie, fav_poster_url, is_favorite=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    movie_similarities = df_final_clean[df_final_clean['id1'] == favorite_movie_id][['id2', 'score']]
    movie_similarities = movie_similarities.sort_values(by='score', ascending=False)
    top_recommendations = movie_similarities.head(top_n).reset_index(drop=True)
    recommended_movies = top_recommendations.merge(movies, left_on='id2', right_on='id', how='left')
    st.markdown('<div class="section-heading">Recommended Movies</div>', unsafe_allow_html=True)
    for _, row in recommended_movies.iterrows():
        movie_data = row.to_dict()
        poster_url = get_movie_poster_url(movie_data['id'])
        render_movie_card(movie_data, poster_url, is_favorite=False)
    return recommended_movies

def main():
    header_html = f"""
    <div class="header-container">
        <div style="flex: 3;">
            <h1 class="title">
                <span style="white-space: nowrap;">Welcome To Your Ultimate</span><br>
                <span style="white-space: nowrap;">Film Emotion Recommender!</span>
            </h1>
            <p class="subtitle">🎬 Find movie recommendations with a similar emotional profile to your favorite movie.<br>🍿 The model is based on sentiment analysis of Rotten Tomatoes reviews.</p>
        </div>
        <div style="flex: 1; display: flex; align-items: center; justify-content: flex-end;">
            <img src="data:image/jpeg;base64,{header_image_base64}" width="350">
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    favorite_movie = st.sidebar.text_input("🎬 Enter the name of your favorite movie:")
    top_n = st.sidebar.slider("🔢 How many recommendations do you want?", 1, 5, 3)
    
    movies, reviews, df_final_clean = load_data()
    if favorite_movie:
        recommend_similar_movies(df_final_clean, movies, reviews, favorite_movie, top_n)

if __name__ == "__main__":
    main()