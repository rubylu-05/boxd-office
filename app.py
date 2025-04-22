import streamlit as st
import pandas as pd
import warnings
from visualizations.ratings.ratings_scatter import plot_ratings_scatter
from visualizations.ratings.ratings_histogram import plot_ratings_histogram
from visualizations.ratings.liked_pie import plot_liked_pie
from visualizations.genres.popular_genres import plot_popular_genres
from visualizations.genres.genre_radar import plot_genre_rating_radar
from visualizations.genres.popular_themes import plot_popular_themes
from visualizations.genres.theme_radar import plot_theme_rating_radar
from visualizations.decades.popular_decades import plot_popular_decades
from visualizations.decades.decade_radar import plot_decades_rating_radar
from visualizations.decades.year_ratings import plot_yearly_average_ratings
from visualizations.runtime.runtime_histogram import plot_runtime_histogram
from visualizations.runtime.runtime_scatter import plot_runtime_scatter
from visualizations.obscurity.members_histogram import plot_members_histogram
from visualizations.obscurity.liked_histogram import plot_liked_histogram
from visualizations.obscurity.ratings_histogram import plot_avg_rating_distribution
from theme import ORANGE, GREEN, BLUE

warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(page_title="Boxd Office", page_icon="🍿", layout="wide")

# sticky sidebar
st.markdown(f"""
<style>
html {{
  scroll-behavior: smooth;
}}

#MainMenu, footer {{visibility: hidden;}}

[data-testid="stSidebar"] > div:first-child {{
  position: relative;
}}

.sidebar-toc {{
  position: sticky;
  top: 0;
  padding-top: 1rem;
  z-index: 999;
  background-color: transparent !important;
}}

.sidebar-toc h3 {{
  color: {GREEN};
  margin-bottom: 0.5rem;
}}

.sidebar-toc ul {{
  list-style: none;
  padding-left: 0;
  margin-top: 0;
}}

.sidebar-toc li {{
  margin-bottom: 0.25rem;
}}

.sidebar-toc a {{
  text-decoration: none;
  color: #ddd;
  font-size: 0.95rem;
}}

.sidebar-toc a:hover {{
  color: {ORANGE};
}}
</style>
""", unsafe_allow_html=True)

# sidebar table of contents
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-toc">
      <h3>Contents</h3>
      <ul>
        <li><a href="#likes-ratings">Likes & Ratings</a></li>
        <li><a href="#genres-themes">Genres & Themes</a></li>
        <li><a href="#decades">Decades</a></li>
        <li><a href="#runtime">Runtime</a></li>
        <li><a href="#obscurity">Obscurity</a></li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

# main app
def load_data(username):
    films_df = pd.read_csv('rubylu.csv')
    for col in ['genres', 'themes', 'cast']:
        films_df[col] = films_df[col].apply(eval)
    return films_df

st.markdown(f"<div style='font-size: 4.5em; font-weight: bold;'><span style='color: {ORANGE};'>Boxd</span>·<span style='color: {GREEN};'>Office</span></div>", unsafe_allow_html=True)
st.write("Visualize your Letterboxd film data!")

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

if 'films_df' in st.session_state:
    films_df = st.session_state['films_df']
    films_df['decade'] = (films_df['year'] // 10) * 10

    csv = films_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data as CSV", data=csv, file_name='letterboxd_data.csv', mime='text/csv')
    st.divider()

    all_decades = sorted(films_df['decade'].unique())
    decades_labels = [f"{d}s" for d in all_decades]
    selected_decades = st.multiselect("Filter by decade:", decades_labels)
    if selected_decades:
        selected_decade_values = [int(d[:-1]) for d in selected_decades]
        filtered_df = films_df[films_df['decade'].isin(selected_decade_values)]
    else:
        filtered_df = films_df

    all_genres = sorted({g for genres in filtered_df['genres'] for g in genres})
    selected_genres = st.multiselect("Filter by genre:", all_genres)
    if selected_genres:
        filtered_df = filtered_df[filtered_df['genres'].apply(lambda genres: any(g in genres for g in selected_genres))]

    # likes & ratings
    st.markdown(f"<a name='likes-ratings'></a><h2 style='color: {GREEN};'>Likes & Ratings</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_ratings_histogram(filtered_df, selected_genres), use_container_width=True)
    with col2:
        st.plotly_chart(plot_liked_pie(filtered_df), use_container_width=True)
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
    st.divider()

    # genres & themes
    st.markdown(f"<a name='genres-themes'></a><h2 style='color: {GREEN};'>Genres & Themes</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_popular_genres(filtered_df), use_container_width=True)
    st.plotly_chart(plot_genre_rating_radar(filtered_df), use_container_width=True)
    st.plotly_chart(plot_popular_themes(filtered_df), use_container_width=True)
    # st.plotly_chart(plot_theme_rating_radar(filtered_df), use_container_width=True)
    st.divider()

    # decades
    st.markdown(f"<a name='decades'></a><h2 style='color: {GREEN};'>Decades</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_popular_decades(filtered_df), use_container_width=True)
    st.plotly_chart(plot_decades_rating_radar(filtered_df), use_container_width=True)
    st.plotly_chart(plot_yearly_average_ratings(filtered_df), use_container_width=True)
    st.divider()

    # runtime
    st.markdown(f"<a name='runtime'></a><h2 style='color: {GREEN};'>Runtime</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_runtime_histogram(films_df), use_container_width=True)
    st.plotly_chart(plot_runtime_scatter(films_df), use_container_width=True)
    st.divider()

    # obscurity
    st.markdown(f"<a name='obscurity'></a><h2 style='color: {GREEN};'>Obscurity</h2>", unsafe_allow_html=True)
    st.plotly_chart(plot_members_histogram(films_df), use_container_width=True)
    st.plotly_chart(plot_liked_histogram(films_df), use_container_width=True)
    st.plotly_chart(plot_avg_rating_distribution(films_df), use_container_width=True)
