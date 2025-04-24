import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from .scrape_film_details import get_film_details

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

def get_films(username, max_threads=10):
    base_url = f"https://letterboxd.com/{username}/films/by/date-earliest/"
    films = []
    film_slug_to_film = {}
    page = 1

    print(f"Starting to scrape films for user: {username}")
    
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
    print(f"\nFound {len(films)} films total. Now getting details...\n")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(get_film_details, film['film_slug']): film['film_slug'] for film in films}
        for future in as_completed(futures):
            slug, details = future.result()
            film_details_map[slug] = details
            title = next((f['title'] for f in films if f['film_slug'] == slug), "Unknown Title")
            print(f"Processed details for: {title}")

    # preserve original order
    final_data = []
    for film in films:
        slug = film['film_slug']
        details = film_details_map.get(slug, {})
        film.update(details)
        final_data.append(film)
    print("\nDone!")
    
    return final_data