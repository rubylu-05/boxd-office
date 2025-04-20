import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter
from scraper import get_film_details, star_to_rating
import numpy as np
import matplotlib.animation as animation
from matplotlib import rcParams
from io import BytesIO
import base64

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']
rcParams['axes.edgecolor'] = '#333F4B'
rcParams['axes.linewidth'] = 0.8
rcParams['xtick.color'] = '#333F4B'
rcParams['ytick.color'] = '#333F4B'

def stream_film_scrape(username, max_pages=None):
    base_url = f"https://letterboxd.com/{username}/films/by/date-earliest/"
    page = 1

    while True:
        url = f"{base_url}page/{page}/" if page > 1 else base_url
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        film_list = soup.find_all('li', class_='poster-container')
        if not film_list:
            break

        for film in film_list:
            title = film.find('img')['alt']
            film_slug = film.find('div')['data-film-slug']
            rating = film.find('span', class_='rating')
            rating = rating.text.strip() if rating else None
            liked = bool(film.find('span', class_='like'))

            film_data = {
                'title': title,
                'liked': liked,
                'rating': star_to_rating.get(rating, None),
                'film_slug': film_slug
            }
            yield film_data

        page += 1
        if max_pages and page > max_pages:
            break

def create_bar_chart_race(genre_counter, current_film):
    top_genres = genre_counter.most_common(10)
    genres = [g[0] for g in top_genres]
    counts = [g[1] for g in top_genres]
    
    sorted_indices = np.argsort(counts)
    genres = [genres[i] for i in sorted_indices]
    counts = [counts[i] for i in sorted_indices]
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.set_facecolor('#f0f0f0')
    fig.patch.set_facecolor('#f0f0f0')
    
    bars = ax.barh(genres, counts, color=plt.cm.tab20c(range(len(genres))))
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', which='both', left=False)
    
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', 
                ha='left', va='center', 
                fontsize=10, color='#333F4B')
    
    ax.set_xlabel('Count', fontsize=12, color='#333F4B')
    ax.set_title(f'Top Genres - Currently Viewing: {current_film}', 
                fontsize=14, color='#333F4B', pad=20)
    
    plt.tight_layout()
    
    return fig

def get_animated_chart(genre_history, film_history):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=200)
    ax.set_facecolor('#f0f0f0')
    fig.patch.set_facecolor('#f0f0f0')
    
    def animate(i):
        ax.clear()
        current_genres = genre_history[i]
        current_film = film_history[i]
        
        top_genres = current_genres.most_common(10)
        genres = [g[0] for g in top_genres]
        counts = [g[1] for g in top_genres]
        
        sorted_indices = np.argsort(counts)
        genres = [genres[i] for i in sorted_indices]
        counts = [counts[i] for i in sorted_indices]
        
        bars = ax.barh(genres, counts, color=plt.cm.tab20c(range(len(genres))))
        
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', which='both', left=False)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', 
                    ha='left', va='center', 
                    fontsize=10, color='#333F4B')
        
        ax.set_xlabel('Count', fontsize=12, color='#333F4B')
        ax.set_title(f'Top Genres - Currently Viewing: {current_film}', 
                    fontsize=14, color='#333F4B', pad=20)
        
        plt.tight_layout()
    
    anim = animation.FuncAnimation(
        fig, animate, frames=len(genre_history), interval=500, repeat=False
    )
    
    temp_file = BytesIO()
    anim.save(temp_file, writer='pillow', fps=2)
    plt.close(fig)
    
    temp_file.seek(0)
    b64 = base64.b64encode(temp_file.read()).decode('utf-8')
    
    return f'<img src="data:image/gif;base64,{b64}" alt="animated genre chart">'

st.title("Boxd Office")

username = st.text_input("Enter your Letterboxd username:")
max_pages = st.slider("Maximum pages to scrape", 1, 20, 5)
start_button = st.button("Start Scraping")

if start_button and username:
    genre_counter = Counter()
    genre_history = []
    film_history = []
    
    status_text = st.empty()
    chart_placeholder = st.empty()
    
    for film in stream_film_scrape(username, max_pages=max_pages):
        status_text.markdown(f"**Currently scraping:** *{film['title']}*")
        
        _, details = get_film_details(film['film_slug'])
        genres = details.get('genres', [])
        genre_counter.update(genres)
        
        genre_history.append(genre_counter.copy())
        film_history.append(film['title'])
        
        fig = create_bar_chart_race(genre_counter, film['title'])
        chart_placeholder.pyplot(fig)
        plt.close(fig)
            
    status_text.success("Scraping complete!")
    
    st.markdown("### Genre Race Animation")
    st.markdown(get_animated_chart(genre_history, film_history), unsafe_allow_html=True)
    
    st.markdown("### Final Genre Counts")
    final_genres = pd.DataFrame(genre_counter.most_common(10), columns=['Genre', 'Count'])
    st.dataframe(final_genres)