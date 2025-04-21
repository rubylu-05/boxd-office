import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(page_title="Boxd Office", page_icon="🎬")

star_to_rating = {
    "★": 1,
    "★★": 2,
    "★★★": 3,
    "★★★★": 4,
    "★★★★★": 5,
    "½": 0.5,
    "★½": 1.5,
    "★★½": 2.5,
    "★★★½": 3.5,
    "★★★★½": 4.5,
    None: None
}

def get_film_details(film_slug):
    def get_digits(text):
        return int(''.join(filter(str.isdigit, text)) or 0)
    
    details = {
        'avg_rating': None,
        'num_watched': None,
        'num_liked': None,
        'year': None,
        'runtime': None,
        'genres': [],
        'themes': [],
        'director': None,
        'cast': []
    }

    try:
        film_url = f"https://letterboxd.com/film/{film_slug}/"
        response = requests.get(film_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # get release year
        year_tag = soup.find('a', href=lambda x: x and '/year/' in x)
        if year_tag:
            details['year'] = year_tag.text.strip()
        
        # get runtime
        runtime = soup.find('p', class_='text-link text-footer')
        if runtime:
            details['runtime'] = get_digits(runtime.get_text(strip=True))
        
        # get genres and themes
        genre_div = soup.find('div', id='tab-genres')
        if genre_div:
            genres = genre_div.find_all('a')
            for a in genres:
                href = a.get('href', '')
                if '/films/genre/' in href:
                    details['genres'].append(a.text)
                elif '/films/theme/' in href or '/films/mini-theme/' in href:
                    details['themes'].append(a.text)
        
        # get director
        director_tag = soup.find('a', href=lambda x: x and '/director/' in x)
        if director_tag:
            details['director'] = director_tag.text
        
        # get cast
        actor_div = soup.find('div', id='tab-cast')
        if actor_div:
            details['cast'] = [a.text for a in actor_div.find_all('a', href=lambda x: x and '/actor/' in x)]

        # get average rating
        ratings_url = f"https://letterboxd.com/csi/film/{film_slug}/rating-histogram/"
        ratings_html = requests.get(ratings_url, timeout=10).text
        rating = BeautifulSoup(ratings_html, 'html.parser').find('a', class_='display-rating')
        if rating:
            details['avg_rating'] = float(rating['title'].split("Weighted average of ")[1].split(" based")[0])
        
        # get stats (watched, liked)
        stats_url = f"https://letterboxd.com/csi/film/{film_slug}/stats/"
        stats_html = requests.get(stats_url, timeout=10).text
        stats_soup = BeautifulSoup(stats_html, 'html.parser')
        
        watched_stat = stats_soup.find('a', class_='icon-watched')
        if watched_stat:
            details['num_watched'] = get_digits(watched_stat['title'])
        
        liked_stat = stats_soup.find('a', class_='icon-liked')
        if liked_stat:
            details['num_liked'] = get_digits(liked_stat['title'])

    except Exception as e:
        st.error(f"Failed to fetch details for {film_slug}: {e}")

    return film_slug, details


def get_films(username, max_threads=10):
    base_url = f"https://letterboxd.com/{username}/films/by/date-earliest/"
    films = []
    film_slug_to_film = {}
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
            films.append(film_data)
            film_slug_to_film[film_slug] = film_data
        page += 1

    st.info(f"Found {len(films)} films. Fetching details...")

    film_details_map = {}
    progress_bar = st.progress(0)
    status_text = st.empty()

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(get_film_details, film['film_slug']): film['film_slug'] for film in films}
        for i, future in enumerate(as_completed(futures)):
            slug, details = future.result()
            film_details_map[slug] = details
            title = film_slug_to_film[slug]['title']
            status_text.text(f"Fetched details for: {title}")
            progress_bar.progress((i + 1) / len(films))

    # preserve original order
    final_data = []
    for film in films:
        slug = film['film_slug']
        details = film_details_map.get(slug, {})
        film.update(details)
        film.pop('film_slug', None)
        final_data.append(film)

    return pd.DataFrame(final_data)

def main():
    st.title("Boxd Office")
    st.write("Visualize your Letterboxd film data!")
    
    with st.form("user_input"):
        username = st.text_input("Enter your Letterboxd username:")
        submit_button = st.form_submit_button("Start")
    
    if submit_button:
        if not username:
            st.error("Please enter a valid Letterboxd username")
            return
            
        with st.spinner("Scraping your films..."):
            try:
                films_df = get_films(username, max_threads=20)
                st.success("Scraping complete!")
                
                st.subheader("Your Film Data")
                st.dataframe(films_df)
                
                csv = films_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f'{username}_letterboxd.csv',
                    mime='text/csv'
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()