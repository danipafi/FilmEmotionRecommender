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

    # Load the similarity matrix in parts
    base_dir = "/Users/danielebelmiro/Data_Analytics_Bootcamp/Rotten/"
    folders = [os.path.join(base_dir, f"similarity_matrix_part_{i}.parquet") for i in range(10)]
    file_paths = [os.path.join(folder, "part.0.parquet") for folder in folders]

    # Check if files exist
    for file in file_paths:
        if not os.path.exists(file):
            st.error(f"File not found: {file}")
            return None, None, None

    # Load the similarity matrix with Dask
    sim_df = dd.read_parquet(file_paths, engine='pyarrow').compute()  # Convert to Pandas DataFrame
    return movies, reviews, sim_df

# Recommendation function
def recommend_similar_movies(sim_df, movies, reviews, favorite_movie, top_n=5):
    movies = movies.copy()

    # Convert the 'genre' column from string to list (if necessary)
    if isinstance(movies['genre'].iloc[0], str):
        movies['genre'] = movies['genre'].apply(ast.literal_eval)

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

    # Check if the movie is in the similarity matrix
    if favorite_movie_id not in sim_df.columns:
        st.error(f"Movie ID '{favorite_movie_id}' not found in the similarity matrix.")
        return None

    # Get similarity scores and sort by highest similarity
    movie_similarities = sim_df[favorite_movie_id].sort_values(ascending=False)
    movie_similarities = movie_similarities.drop(favorite_movie_id, errors='ignore')

    # Filter recommendations by genre
    favorite_movie_genres = set(matching_movies['genre'].explode().values)
    st.write(f"Movie genres: {', '.join(favorite_movie_genres)}")

    recommended_ids = movies[movies['genre'].apply(lambda genres: any(genre in favorite_movie_genres for genre in genres))]['id'].unique()
    movie_similarities = movie_similarities[movie_similarities.index.isin(recommended_ids)]

    # Top N recommendations
    top_recommendations = movie_similarities.head(top_n).reset_index()
    top_recommendations.columns = ['id', 'similarity']

    # Merge with movie details
    recommended_movies = top_recommendations.merge(movies, on='id', how='left')

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
            st.write(f"   🔗 **Similarity Score:** {row['similarity']:.5f}")
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
    st.title("Movie Recommendation System")

    # Load data
    movies, reviews, sim_df = load_data()

    # User input
    favorite_movie = st.text_input("Enter the name of your favorite movie:")
    top_n = st.slider("How many recommendations do you want?", 1, 10, 5)

    if favorite_movie:
        recommend_similar_movies(sim_df, movies, reviews, favorite_movie, top_n)

# Run the application
if __name__ == "__main__":
    main()


# In[ ]:




