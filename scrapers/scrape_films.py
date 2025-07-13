import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from .scrape_film_details import get_film_details
import functools

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}
BASE_DELAY = 1.5  # delay between requests
MAX_RETRIES = 3
MAX_THREADS = 5
DEBUG = False

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

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def make_request(url):
    """Optimized request function with retries and jittered delays"""
    for attempt in range(MAX_RETRIES):
        try:            
            response = SESSION.get(url, timeout=10)
            response.raise_for_status()
            
            if response.status_code == 403 or "403 Forbidden" in response.text:
                raise requests.exceptions.RequestException("403 Forbidden - Possible block")
                
            return response
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            wait_time = (2 ** attempt) + random.random()
            time.sleep(wait_time)

def get_films(username):
    base_url = f"https://letterboxd.com/{username}/films/"
    films = []
    page = 1
    
    print(f"\n{'='*50}\nScraping film list for @{username}\n{'='*50}")
    
    while True:
        try:
            url = f"{base_url}page/{page}/" if page > 1 else base_url
            if DEBUG:
                print(f"\nPage {page}: {url}")
            
            response = make_request(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            film_list = soup.find_all('li', class_='poster-container')
            
            if not film_list:
                if DEBUG:
                    print("No more films found")
                break

            page_films = []
            for film in film_list:
                img = film.find('img')
                div = film.find('div')
                rating = film.find('span', class_='rating')
                
                film_data = {
                    'title': img['alt'] if img else 'Unknown',
                    'liked': bool(film.find('span', class_='like')),
                    'rating': star_to_rating.get(rating.text.strip() if rating else None, None),
                    'film_slug': div['data-film-slug'] if div else None
                }
                if film_data['film_slug']:
                    page_films.append(film_data)
            
            films.extend(page_films)
            if DEBUG:
                print(f"Added {len(page_films)} films from page {page}")
            
            next_link = soup.find('a', class_='next')
            if not next_link:
                break
                
            page += 1
            
            delay = BASE_DELAY + (0.5 if page % 5 == 0 else 0) + random.uniform(0, 1)
            if DEBUG:
                print(f"Waiting {delay:.1f}s before next page...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"Error on page {page}: {str(e)[:200]}")
            break
    
    film_details = {}
    total_films = len(films)
    
    detail_func = functools.partial(get_film_details, session=SESSION)
    
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(detail_func, film['film_slug']): film['film_slug'] for film in films}
        
        for i, future in enumerate(as_completed(futures), 1):
            slug = futures[future]
            try:
                _, details = future.result()
                film_details[slug] = details
                title = next((f['title'] for f in films if f['film_slug'] == slug), "Unknown")
                
                if DEBUG and i % 10 == 0:
                    print(f"Processed {i}/{total_films}: {title[:30]}...")
                
            except Exception as e:
                print(f"Failed to process {slug}: {str(e)[:200]}")
            
            if i % 20 == 0:
                delay = 1 + random.random()
                if DEBUG:
                    print(f"Pause ({delay:.1f}s)\n")
                time.sleep(delay)

    final_data = []
    for film in films:
        slug = film['film_slug']
        details = film_details.get(slug, {})
        combined = {**film, **details}
        final_data.append(combined)
    
    return final_data
