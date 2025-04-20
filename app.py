import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter
from scraper import get_film_details, star_to_rating

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

def show_bar_chart_race(genre_counter):
    top_genres = genre_counter.most_common(10)
    genres, counts = zip(*top_genres)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(genres, counts, color='skyblue')
    ax.set_xlabel('Count')
    ax.set_title('Top Genres (Live)')
    st.pyplot(fig)

st.title("Boxd Office")

username = st.text_input("Enter your Letterboxd username:")
start_button = st.button("Start")

if start_button and username:
    genre_counter = Counter()
    placeholder_text = st.empty()
    chart_placeholder = st.empty()

    for film in stream_film_scrape(username, max_pages=10):
        placeholder_text.write(f"Scraping: {film['title']}...")

        _, details = get_film_details(film['film_slug'])
        genres = details.get('genres', [])
        genre_counter.update(genres)

        chart_placeholder.empty()
        show_bar_chart_race(genre_counter)

        time.sleep(0.1)

    placeholder_text.success("Done!")