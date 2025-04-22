import streamlit as st
import pandas as pd
import warnings
from visualizations.ratings.ratings_scatter import plot_ratings_scatter
from visualizations.genres.popular_genres import plot_popular_genres
from visualizations.genres.genre_radar import plot_genre_rating_radar
from visualizations.genres.popular_themes import plot_popular_themes
from visualizations.genres.theme_radar import plot_theme_rating_radar
from visualizations.decades.popular_decades import plot_popular_decades
from visualizations.decades.decade_radar import plot_decades_rating_radar
from visualizations.decades.year_ratings import plot_yearly_average_ratings
from theme import ORANGE, GREEN, BLUE

warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(page_title="Boxd Office", page_icon="🍿")

def load_data(username):
    films_df = pd.read_csv('rubylu.csv')
    for col in ['genres', 'themes', 'cast']:
        films_df[col] = films_df[col].apply(eval)
    return films_df

# page header
st.markdown(f"<h1 style='font-size: 4em;'><span style='color: {ORANGE};'>Boxd</span>·<span style='color: {GREEN};'>Office</span></h1>", unsafe_allow_html=True)
st.write("Visualize your Letterboxd film data!")

# username input
if 'films_df' not in st.session_state:
    with st.form("user_input"):
        username = st.text_input("Enter your Letterboxd username:")
        submit_button = st.form_submit_button("Start")

        if submit_button:
            if not username:
                st.error("Please enter a valid Letterboxd username")
            else:
                with st.spinner("Loading your films..."):
                    try:
                        st.session_state['films_df'] = load_data(username)
                        st.success("Data loaded successfully!")
                    except Exception as e:
                        st.error(f"Failed to load data: {e}")
                        st.stop()

# main app logic (after data loads)
if 'films_df' in st.session_state:
    films_df = st.session_state['films_df']

    st.markdown(f"<h3 style='color: {BLUE}; font-weight: bold;'>Your Film Data</h3>", unsafe_allow_html=True)
    st.dataframe(films_df)

    csv = films_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f'letterboxd_data.csv',
        mime='text/csv'
    )

    st.markdown(f"<h2 style='color: {GREEN};'>Your Ratings</h2>", unsafe_allow_html=True)

    all_genres = sorted({genre for genres in films_df['genres'] for genre in genres})
    selected_genres = st.multiselect("Filter by genre:", options=all_genres)

    if selected_genres:
        filtered_df = films_df[films_df['genres'].apply(lambda genres: any(g in genres for g in selected_genres))]
    else:
        filtered_df = films_df

    st.plotly_chart(plot_ratings_scatter(filtered_df, selected_genres), use_container_width=True)

    st.markdown(f"<h2 style='color: {GREEN};'>Genres and Themes</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_popular_genres(films_df), use_container_width=True)
    st.plotly_chart(plot_genre_rating_radar(films_df), use_container_width=True)
    st.plotly_chart(plot_popular_themes(films_df), use_container_width=True)
    st.plotly_chart(plot_theme_rating_radar(films_df), use_container_width=True)

    st.markdown(f"<h2 style='color: {GREEN};'>Decades</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_popular_decades(films_df), use_container_width=True)
    st.plotly_chart(plot_decades_rating_radar(films_df), use_container_width=True)
    st.plotly_chart(plot_yearly_average_ratings(films_df), use_container_width=True)
