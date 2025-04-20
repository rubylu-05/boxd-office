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
    "★★★★½": 4.5,
    None: None
}

def get_films(username):
    base_url = f"https://letterboxd.com/{username}/films/by/date-earliest/"
    films = {
        'title': [],
        'liked': [],
        'rating': [],
        'avg_rating': [],
        'num_watched': [],
        'num_liked': [],
        'year': [],
        'runtime': [],
        'genres': [],
        'themes': [],
        'director': [],
        'cast': [],
    }
    
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
            liked = bool(film.find('span', class_='like'))
            film_details = get_film_details(film_url)
            
            films['title'].append(title)
            films['liked'].append(liked)
            films['rating'].append(star_to_rating[rating])
            films['avg_rating'].append(film_details['avg_rating'])
            films['num_watched'].append(film_details['num_watched'])
            films['num_liked'].append(film_details['num_liked'])
            films['year'].append(film_details['year'])
            films['runtime'].append(film_details['runtime'])
            films['genres'].append(film_details['genres'])
            films['themes'].append(film_details['themes'])
            films['director'].append(film_details['director'])
            films['cast'].append(film_details['cast'])
            
            print(film_url)
                
        page += 1
    
    return pd.DataFrame(films)

def get_film_details(film_slug):
    def get_digits(text):
        return ''.join(filter(str.isdigit, text))
    
    film_url = f"https://letterboxd.com/film/{film_slug}/"
    response = requests.get(film_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    details = {}
    
    # get release year
    details['year'] = soup.find('a', href=lambda x: x and '/year/' in x).text.strip()
    
    # get runtime
    runtime = soup.find('p', class_='text-link text-footer')
    details['runtime'] = int(get_digits(runtime.get_text(strip=True)))
    
    # get genres
    genres = []
    genre_div = soup.find('div', id='tab-genres')
    if genre_div:
        genres = [a.text for a in genre_div.find_all('a', href=lambda x: x and '/films/genre/' in x)]
    details['genres'] = genres
    
    # get themes
    themes = []
    theme_div = soup.find('div', id='tab-genres')
    if theme_div:
        themes = [a.text for a in theme_div.find_all('a', href=lambda x: x and ('/films/theme/' in x or 'films/mini-theme/' in x))]    
    details['themes'] = themes
    
    # get director
    details['director'] = soup.find('a', href=lambda x: x and '/director/' in x).text
    
    # get cast
    actors = []
    actor_div = soup.find('div', id='tab-cast')
    if actor_div:
        actors = [a.text for a in actor_div.find_all('a', href=lambda x: x and '/actor/' in x in x)]    
    details['cast'] = actors
    
    # get community stats
    ratings_url = f"https://letterboxd.com/csi/film/{film_slug}/rating-histogram/"
    ratings = BeautifulSoup(requests.get(ratings_url).text, 'html.parser')
    rating = ratings.find('a', class_='display-rating')['title']
    details['avg_rating'] = float(rating.split("Weighted average of ")[1].split(" based")[0])
    
    film_stats_url = f"https://letterboxd.com/csi/film/{film_slug}/stats/"
    film_stats = BeautifulSoup(requests.get(film_stats_url).text, 'html.parser')
            
    # number of members watched
    watched_stat = film_stats.find('a', class_='icon-watched')
    details['num_watched'] = int(get_digits(watched_stat['title']))
    
    # number of members liked
    liked_stat = film_stats.find('a', class_='icon-liked')
    details['num_liked'] = int(get_digits(liked_stat['title']))
    
    return details

films_df = get_films('rubylu')
print(films_df)
films_df.to_csv('rubylu.csv', index=False)