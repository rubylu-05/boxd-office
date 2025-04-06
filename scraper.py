import requests
from bs4 import BeautifulSoup
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
    "★★★★½": 4.5
}

def get_rated_films(username):
    base_url = f"https://letterboxd.com/{username}/films/"
    films = []
    
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
        
        # get ratings
        for film in film_list:
            title = film.find('img')['alt']
            film_url = film.find('div')['data-film-slug']
            rating = film.find('span', class_='rating')
            rating = rating.text.strip() if rating else None
            
            films.append({
                'title': title,
                'film_url': film_url,
                'rating': star_to_rating[rating]
            })
        
        page += 1
    
    return pd.DataFrame(films)

def get_film_details(film_slug):
    film_url = f"https://letterboxd.com/film/{film_slug}/"
    response = requests.get(film_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    details = {}
    
    # get release year
    year = soup.find('a', href=lambda x: x and '/year/' in x)
    details['year'] = year.text.strip() if year else None
    
    # get genres
    genres = []
    genre_div = soup.find('div', id='tab-genres')
    if genre_div:
        genres = [a.text for a in genre_div.find_all('a', href=lambda x: x and '/films/genre/' in x)]
    details['genres'] = genres
    
    # get director
    director = soup.find('a', href=lambda x: x and '/director/' in x)
    details['director'] = director.text if director else None
    
    return details

films_df = get_rated_films('rubylu')
# print(films_df)