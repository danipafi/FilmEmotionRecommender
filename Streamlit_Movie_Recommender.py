import pandas as pd
import dask.dataframe as dd
import os
import re
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup
import ast  # Import necessário para conversão de string para lista/tupla

# Function to normalize names
def normalize_name(name):
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)  # Remove special characters
    name = name.lower().strip()  # Convert to lowercase and remove extra spaces
    return name

# Function to generate the Rotten Tomatoes URL based on the movie ID
def generate_rotten_tomatoes_url(movie_id):
    return f"https://www.rottentomatoes.com/m/{movie_id}"

# Function to extract the movie poster URL from the photos page


def get_movie_poster_url(movie_id):
    # Acessa a página principal do filme, que geralmente contém a meta tag "og:image"
    url = f"https://www.rottentomatoes.com/m/{movie_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tenta extrair a URL do pôster pela meta tag "og:image"
    meta_tag = soup.find('meta', property="og:image")
    if meta_tag and meta_tag.get('content'):
        return meta_tag['content']
    
    # Se não encontrar pela meta tag, tenta buscar a imagem pela classe antiga
    poster_img = soup.find('img', {'class': 'posterImage'})
    if poster_img and 'src' in poster_img.attrs:
        return poster_img['src']
    
    return None


# Function to load and display movie posters
def display_poster(poster_url):
    if poster_url:
        try:
            response = requests.get(poster_url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                st.image(img, width=150)  # Display the image
            else:
                st.write("Poster not available")  # If the URL is invalid
        except Exception as e:
            st.write(f"Error loading poster: {e}")  # If there's an error loading the image
    else:
        st.write("Poster not available")  # If the URL is missing

# Load data
@st.cache_data
def load_data():
    # Load DataFrames
    reviews = pd.read_csv('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/reviews_emotions.csv')
    movies = pd.read_csv('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/movies_final.csv')

    # Converter as colunas 'genre' e 'emotions' de string para lista/tupla
    movies['genre'] = movies['genre'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    movies['emotions'] = movies['emotions'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # Carregar a matriz reduzida
    df_final = dd.read_parquet('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/processed_chunks').compute()  # Convertendo para pandas para facilitar a validação
    
    return movies, reviews, df_final

# Recommendation function
def recommend_similar_movies(df_final, movies, reviews, favorite_movie, top_n=5):
    movies = movies.copy()

    # Normalize the movie name
    favorite_movie_normalized = normalize_name(favorite_movie)

    # Find the movie in the dataset
    matching_movies = movies[movies['title_normalized'] == favorite_movie_normalized]
    if matching_movies.empty:
        st.error(f"The movie '{favorite_movie}' was not found. Please check the name and try again.")
        return None

    favorite_movie_id = matching_movies.iloc[0]['id']
    favorite_movie_title = matching_movies.iloc[0]['title']
    st.success(f"Movie found: {favorite_movie_title} (ID: {favorite_movie_id})")

    # Get similarity scores and sort by highest similarity
    movie_similarities = df_final[df_final['id1'] == favorite_movie_id][['id2', 'score']]
    movie_similarities = movie_similarities.sort_values(by='score', ascending=False)

    # Top N recommendations
    top_recommendations = movie_similarities.head(top_n).reset_index(drop=True)

    # Merge with movie details
    recommended_movies = top_recommendations.merge(movies, left_on='id2', right_on='id', how='left')

    # Display the emotional profile of the favorite movie
    favorite_movie_emotions = matching_movies.iloc[0]['emotions']
    st.subheader(f"Emotional profile of '{favorite_movie_title}':")
    st.write(
        ", ".join([f"{mood}: {percentage:.1f}%" for mood, percentage in favorite_movie_emotions])
    )
    
    # Display recommendations
    st.subheader(f"Top {top_n} recommendations based on '{favorite_movie_title}':")
    for _, row in recommended_movies.iterrows():
        col1, col2 = st.columns([1, 3])  # Split into two columns for poster and details
        with col1:
            # Extract and display the movie poster
            poster_url = get_movie_poster_url(row['id'])
            display_poster(poster_url)
        with col2:
            st.write(f"🎬 **Movie:** {row['title']}")
            st.write(f"   🎬 **Director:** {row['director']}")
            st.write(f"   🌍 **Language:** {row['originalLanguage']}")
            st.write(f"   ⏳ **Duration:** {row['runtimeMinutes']} min")
            st.write(
                f"   🎭 **Genre:** {', '.join(row['genre']) if isinstance(row['genre'], (list, tuple)) else row['genre']}"
            )
            st.write(f"   📅 **Year:** {row['release_year']}")
            st.write(f"   🍅 **Tomatometer:** {row['tomatoMeter']}%")
            st.write(f"   🎟️ **Audience Score:** {row['audienceScore']}%")
            st.write(f"   🔗 **Similarity Score:** {row['score']:.5f}")
            st.write(
                f"   ❤️ **Emotional Profile:** {', '.join([f'{mood}: {percentage:.1f}%' for mood, percentage in row['emotions']]) if isinstance(row['emotions'], (list, tuple)) else row['emotions']}"
            )

            # Add link to Rotten Tomatoes using the movie ID
            rotten_tomatoes_url = generate_rotten_tomatoes_url(row['id'])
            st.write(f"   🍅 [Link to Rotten Tomatoes]({rotten_tomatoes_url})")
        
        st.write("-" * 50)

    return recommended_movies

# Streamlit interface
def main():
    # Custom CSS for the title
    st.markdown(
        """
        <style>
        .title {
            font-size: 50px;
            text-align: center;
            color: #FF4B4B;
            font-family: 'Arial', sans-serif;
            margin-bottom: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Apply the CSS class to the title
    st.markdown(
        '<h1 class="title">🎬 Movie Recommendation System</h1>',
        unsafe_allow_html=True
    )

    # Load data
    movies, reviews, df_final = load_data()

    # User input for recommendations
    favorite_movie = st.text_input("Enter the name of your favorite movie:")
    top_n = st.slider("How many recommendations do you want?", 1, 5, 3)

    if favorite_movie:
        recommend_similar_movies(df_final, movies, reviews, favorite_movie, top_n)

# Run the application
if __name__ == "__main__":
    main()
