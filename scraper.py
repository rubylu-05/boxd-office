import requests
from bs4 import BeautifulSoup
import pandas as pd

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
            
        for film in film_list:
            title = film.find('img')['alt']
            film_url = film.find('div')['data-film-slug']
            rating = film.find('span', class_='rating')
            rating = rating.text.strip() if rating else None
            
            films.append({
                'title': title,
                'film_url': film_url,
                'rating': rating
            })
        
        page += 1
    
    return pd.DataFrame(films)

films_df = get_rated_films('rubylu')
print(films_df)