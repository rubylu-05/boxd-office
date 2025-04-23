import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

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
        return int(''.join(filter(str.isdigit, text))) or 0
    
    details = {
        'avg_rating': None,
        'num_watched': None,
        'num_liked': None,
        'year': None,
        'runtime': None,
        'genres': [],
        'themes': [],
        'directors': [],
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
        director_div = soup.find('div', id='tab-crew')
        if director_div:
            details['directors'] = [a.text for a in director_div.find_all('a', href=lambda x: x and '/director/' in x)]
        
        # get cast (limit to first 12 actors)
        actor_div = soup.find('div', id='tab-cast')
        if actor_div:
            actor_links = actor_div.find_all('a', href=lambda x: x and '/actor/' in x)
            details['cast'] = [a.text for a in actor_links[:12]]

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
        print(f"Failed to fetch details for {film_slug}: {e}")

    return film_slug, details


def get_films(username, max_threads=20):
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

    film_details_map = {}

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(get_film_details, film['film_slug']): film['film_slug'] for film in films}
        for future in as_completed(futures):
            slug, details = future.result()
            film_details_map[slug] = details

    # preserve original order
    final_data = []
    for film in films:
        slug = film['film_slug']
        details = film_details_map.get(slug, {})
        film.update(details)
        film.pop('film_slug', None)
        final_data.append(film)
    
    df = pd.DataFrame(final_data)
    df.to_csv('rubylu.csv', index=False)
    
    return final_data

get_films("rubylu")