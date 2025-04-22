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
from visualizations.ratings.ratings_histogram import plot_ratings_histogram
from visualizations.ratings.ratings_pie import plot_ratings_pie
from visualizations.runtime.runtime_histogram import plot_runtime_histogram
from theme import ORANGE, GREEN, BLUE

warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(page_title="Boxd Office", page_icon="🍿")

def load_data(username):
    films_df = pd.read_csv('rubylu.csv')
    for col in ['genres', 'themes', 'cast']:
        films_df[col] = films_df[col].apply(eval)
    return films_df

# page header
st.markdown(f"<h1 style='font-size: 4.5em;'><span style='color: {ORANGE};'>Boxd</span>·<span style='color: {GREEN};'>Office</span></h1>", unsafe_allow_html=True)
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

    films_df['decade'] = (films_df['year'] // 10) * 10

    st.markdown(f"<h3 style='color: {BLUE}; font-weight: bold;'>Your Film Data</h3>", unsafe_allow_html=True)
    st.dataframe(films_df)

    csv = films_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f'letterboxd_data.csv',
        mime='text/csv'
    )
    st.markdown('##')

    st.markdown(f"<h2 style='color: {GREEN};'>Likes and Ratings</h2>", unsafe_allow_html=True)

    # decade filter
    all_decades = sorted(films_df['decade'].unique())
    decades_labels = [f"{decade}s" for decade in all_decades]
    selected_decades = st.multiselect("Filter by decade:", options=decades_labels, key="decades_filter")
    if selected_decades:
        selected_decade_values = [int(decade[:-1]) for decade in selected_decades]
        filtered_df = films_df[films_df['decade'].isin(selected_decade_values)]
    else:
        filtered_df = films_df

    # genre filter
    all_genres = sorted({genre for genres in filtered_df['genres'] for genre in genres})
    selected_genres = st.multiselect("Filter by genre:", options=all_genres, key="genres_filter")

    if selected_genres:
        filtered_df = filtered_df[filtered_df['genres'].apply(lambda genres: any(g in genres for g in selected_genres))]

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_ratings_histogram(filtered_df, selected_genres), use_container_width=True)
    with col2:
        st.plotly_chart(plot_ratings_pie(filtered_df), use_container_width=True)

    st.plotly_chart(plot_ratings_scatter(filtered_df, selected_genres), use_container_width=True)

    st.markdown(f"<h3 style='color: {BLUE}; font-weight: bold;'>Outliers</h3>", unsafe_allow_html=True)
    outliers_df = filtered_df.dropna(subset=['rating', 'avg_rating']).copy()
    if not outliers_df.empty:
        outliers_df['diff'] = (outliers_df['rating'] - outliers_df['avg_rating']).abs()
        top_outliers = outliers_df.sort_values(by='diff', ascending=False).head(5)

        for _, row in top_outliers.iterrows():
            direction = "higher" if row['rating'] > row['avg_rating'] else "lower"
            diff = round(abs(row['rating'] - row['avg_rating']), 2)
            st.markdown(f"""
                You rated <span style='font-style: italic;'>{row['title']} ({row['year']})</span> 
                <span style='font-weight: bold; color: {BLUE};'>{diff} {direction}</span> than the average Letterboxd user.
            """, unsafe_allow_html=True)
    else:
        st.write("No outliers found for the selected genre(s).")
    st.markdown('##')

    st.markdown(f"<h2 style='color: {GREEN};'>Genres and Themes</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_popular_genres(filtered_df), use_container_width=True)
    st.plotly_chart(plot_genre_rating_radar(filtered_df), use_container_width=True)
    st.plotly_chart(plot_popular_themes(filtered_df), use_container_width=True)
    # st.plotly_chart(plot_theme_rating_radar(filtered_df), use_container_width=True)
    st.markdown('##')

    st.markdown(f"<h2 style='color: {GREEN};'>Decades</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_popular_decades(filtered_df), use_container_width=True)
    st.plotly_chart(plot_decades_rating_radar(filtered_df), use_container_width=True)
    st.plotly_chart(plot_yearly_average_ratings(filtered_df), use_container_width=True)
    st.markdown('##')
    
    st.markdown(f"<h2 style='color: {GREEN};'>Runtime</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_runtime_histogram(films_df), use_container_width=True)
