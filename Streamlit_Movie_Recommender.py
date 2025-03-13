#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import dask.dataframe as dd
import os
import re
import ast
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup

# Function to normalize names
def normalize_name(name):
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)  # Remove special characters
    name = name.lower().strip()  # Convert to lowercase and remove extra spaces
    return name

# Function to generate the Rotten Tomatoes URL based on the movie ID
def generate_rotten_tomatoes_url(movie_id):
    return f"https://www.rottentomatoes.com/m/{movie_id}"

# Function to extract the movie poster URL
def get_movie_poster_url(movie_id):
    url = f"https://www.rottentomatoes.com/m/{movie_id}/pictures"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    poster_div = soup.find('div', {'class': 'movie_poster'})
    if poster_div:
        img_tag = poster_div.find('img')
        if img_tag:
            return img_tag['src']
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
        except:
            st.write("Poster not available")  # If there's an error loading the image
    else:
        st.write("Poster not available")  # If the URL is missing

# Load data
@st.cache_data
def load_data():
    # Load DataFrames
    reviews = pd.read_csv('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/reviews_emotions.csv')
    movies = pd.read_csv('/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/movies_final.csv')

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
    if isinstance(favorite_movie_emotions, list):
        st.write(f"   ❤️ Emotions: {', '.join([f'{mood} ({percentage:.1f}%)' for mood, percentage in favorite_movie_emotions])}")
    else:
        st.write(f"   ❤️ Emotions: {favorite_movie_emotions}")

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
            st.write(f"   🎭 **Genre:** {', '.join(row['genre'])}")
            st.write(f"   📅 **Year:** {row['release_year']}")
            st.write(f"   🍅 **Tomatometer:** {row['tomatoMeter']}%")
            st.write(f"   🎟️ **Audience Score:** {row['audienceScore']}%")
            st.write(f"   🔗 **Similarity Score:** {row['score']:.5f}")
            if isinstance(row['emotions'], list):
                st.write(f"   ❤️ **Emotions:** {', '.join([f'{mood} ({percentage:.1f}%)' for mood, percentage in row['emotions']])}")
            else:
                st.write(f"   ❤️ **Emotions:** {row['emotions']}")
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


# In[ ]:




