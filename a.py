import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie details from API
def fetch_movie_details(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=f0876dce92dd28505b9ec945cb32c688&append_to_response=credits')
    data = response.json()
    credits = data['credits']
    cast = credits['cast']
    crew = credits['crew']
    actor = [actor['name'] for actor in cast if actor['gender'] == 2][0] if any(actor['gender'] == 2 for actor in cast) else "N/A"
    actress = [actress['name'] for actress in cast if actress['gender'] == 1][0] if any(actress['gender'] == 1 for actress in cast) else "N/A"
    director = [person['name'] for person in crew if person['job'] == 'Director'][0] if any(person['job'] == 'Director' for person in crew) else "N/A"
    actor_image = f"https://image.tmdb.org/t/p/original/{[actor['profile_path'] for actor in cast if actor['gender'] == 2][0]}" if any(actor['gender'] == 2 for actor in cast) else None
    actress_image = f"https://image.tmdb.org/t/p/original/{[actress['profile_path'] for actress in cast if actress['gender'] == 1][0]}" if any(actress['gender'] == 1 for actress in cast) else None
    director_image = f"https://image.tmdb.org/t/p/original/{[person['profile_path'] for person in crew if person['job'] == 'Director'][0]}" if any(person['job'] == 'Director' for person in crew) else None
    return {
        'title': data['title'],
        'poster_path': f"https://image.tmdb.org/t/p/original/{data['poster_path']}",
        'overview': data['overview'],
        'release_date': data['release_date'],
        'genres': [genre['name'] for genre in data['genres']],
        'vote_average': data['vote_average'],
        'actor': actor,
        'actress': actress,
        'director': director,
        'actor_image': actor_image,
        'actress_image': actress_image,
        'director_image': director_image
    }

# Function to recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_movie_details = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        movie_details = fetch_movie_details(movie_id)
        recommend_movies.append(movie_details['title'])
        recommend_movie_details.append(movie_details)
    return recommend_movies, recommend_movie_details

# Load movie data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

# Set app title and crafted byline
st.markdown(
    """
    <div style='text-align: center;'>
        <h1 style='font-size: 48px;'>Filmy Rex</h1>
        <h3 style='font-size: 18px;'>Crafted by Arth</h3>
        <h2 style='font-size: 24px;'>🎬 Discover Your Next Favorite Movie!</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Set background image using HTML
st.markdown(
    """
    <style>
    body {
        background-image: url('background.jpg');
        background-size: cover;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Select a movie from the dropdown
selected_movie_name = st.selectbox(
    'Find the perfect movie for your mood! Select one from the list below:',
    movies['title'].values)

st.markdown("""
        **Note:** If you encounter issues with the application
        ,it could be due to the usage of a freely available API key, which may have reached its usage limit.
    """)

# Show information about the selected movie
st.markdown(f"## Your selected movie is {selected_movie_name}")
selected_movie_details = fetch_movie_details(movies[movies['title'] == selected_movie_name].iloc[0]['movie_id'])
st.image(selected_movie_details['poster_path'], use_column_width=True)
st.write(f"**Release Date:** {selected_movie_details['release_date']}")
st.write(f"**Genres:** {', '.join(selected_movie_details['genres'])}")
st.write(f"**Average Rating:** {selected_movie_details['vote_average']}")
st.write(f"**Overview:** {selected_movie_details['overview']}")
st.write("**Top Cast:**")
st.write(f"**Actor:** {selected_movie_details['actor']}", end="")
if selected_movie_details['actor_image']:
    st.image(selected_movie_details['actor_image'], caption=f"{selected_movie_details['actor']}", width=150)
st.write(f"**Actress:** {selected_movie_details['actress']}", end="")
if selected_movie_details['actress_image']:
    st.image(selected_movie_details['actress_image'], caption=f"{selected_movie_details['actress']}", width=150)
st.write(f"**Director:** {selected_movie_details['director']}", end="")
if selected_movie_details['director_image']:
    st.image(selected_movie_details['director_image'], caption=f"{selected_movie_details['director']}", width=150)

# Button to trigger recommendations
if st.button('Recommend'):
    st.markdown(f"## Based on your selection for the movie: {selected_movie_name}, we can recommend you below movies")
    names, details = recommend(selected_movie_name)
    for movie_name, movie_details in zip(names, details):
        st.subheader(movie_name)
        st.image(movie_details['poster_path'], use_column_width=True)
        st.write(f"**Release Date:** {movie_details['release_date']}")
        st.write(f"**Genres:** {', '.join(movie_details['genres'])}")
        st.write(f"**Average Rating:** {movie_details['vote_average']}")
        st.write(f"**Overview:** {movie_details['overview']}")
        st.write("**Top Cast:**")
        st.write(f"**Actor:** {movie_details['actor']}", end="  ")
        if movie_details['actor_image']:
            st.image(movie_details['actor_image'], caption=f"{movie_details['actor']}", width=150)
        st.write(f"**Actress:** {movie_details['actress']}", end="  ")
        if movie_details['actress_image']:
            st.image(movie_details['actress_image'], caption=f"{movie_details['actress']}", width=150)
        st.write(f"**Director:** {movie_details['director']}", end="  ")
        if movie_details['director_image']:
            st.image(movie_details['director_image'], caption=f"{movie_details['director']}", width=150)
        st.markdown("---")
