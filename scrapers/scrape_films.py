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
BASE_DELAY = 0.1
MAX_RETRIES = 2   
MAX_THREADS = 12       # threads for parallel processing
MAX_PAGE_THREADS = 6   # threads for page scraping
DEBUG = True

star_to_rating = {
    "★": 1, "★★": 2, "★★★": 3, "★★★★": 4, "★★★★★": 5,
    "½": 0.5, "★½": 1.5, "★★½": 2.5, "★★★½": 3.5, "★★★★½": 4.5,
    None: None
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def make_request(url):
    for attempt in range(MAX_RETRIES):
        try:
            response = SESSION.get(url, timeout=5)
            response.raise_for_status()
            
            if response.status_code == 403 or "403 Forbidden" in response.text:
                raise requests.exceptions.RequestException("403 Forbidden - Possible block")
                
            return response
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            # wait times between retries
            wait_time = (1.2 ** attempt) + random.random() * 0.3
            time.sleep(wait_time)

def scrape_films_page(url):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        film_list = soup.find_all('li', class_='griditem')
        
        page_films = []
        for film in film_list:
            try:
                react_component = film.find('div', class_='react-component')
                if not react_component:
                    continue
                
                film_slug = react_component.get('data-item-slug')
                if not film_slug:
                    continue
                
                film_title = react_component.get('data-item-name', 'Unknown')
                
                # extracting ratings and likes
                viewing_data = film.find('p', class_='poster-viewingdata')
                rating = None
                liked = False
                
                if viewing_data:
                    rating_span = viewing_data.find('span', class_='rating')
                    if rating_span:
                        rating_text = rating_span.get_text(strip=True)
                        rating = star_to_rating.get(rating_text, None)
                    
                    like_span = viewing_data.find('span', class_='like')
                    if like_span:
                        liked = 'icon-liked' in ' '.join(like_span.get('class', []))
                
                page_films.append({
                    'title': film_title,
                    'liked': liked,
                    'rating': rating,
                    'film_slug': film_slug
                })
                
            except Exception as e:
                if DEBUG:
                    print(f"Error parsing individual film: {str(e)}")
                continue
        
        return page_films, soup.find('a', class_='next') is not None
        
    except Exception as e:
        print(f"Error scraping page {url}: {str(e)[:200]}")
        return [], False

def get_total_pages(base_url):
    try:
        response = make_request(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # check pagination links
        pagination = soup.find('div', class_='paginate-pages')
        if pagination:
            links = pagination.find_all('a')
            if links:
                last_page = max(int(link.text) for link in links if link.text.isdigit())
                return last_page
        
        # estimate from film count
        film_count_elem = soup.find('span', class_='js-former-count')
        if film_count_elem:
            film_count = int(film_count_elem.text.replace(',', ''))
            # assuming ~24 films per page
            return max(1, (film_count + 23) // 24)
            
    except Exception as e:
        if DEBUG:
            print(f"Couldn't determine total pages: {e}")
    
    return 1  # fallback to single page

def get_films(username):
    base_url = f"https://letterboxd.com/{username}/films/"
    films = []
    
    print(f"\n{'='*50}\nScraping film list for @{username}\n{'='*50}")
    
    # determine total pages
    total_pages = get_total_pages(base_url)
    if DEBUG:
        print(f"Detected {total_pages} total pages")
    
    # generate all page URLs
    page_urls = [base_url] + [f"{base_url}page/{page}/" for page in range(2, total_pages + 1)]
    
    # scrape all pages in parallel with minimal delays
    with ThreadPoolExecutor(max_workers=MAX_PAGE_THREADS) as executor:
        future_to_url = {executor.submit(scrape_films_page, url): url for url in page_urls}
        
        completed = 0
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                page_films, has_next = future.result()
                films.extend(page_films)
                completed += 1
                
                if DEBUG:
                    print(f"Scraped {url}: {len(page_films)} films ({completed}/{len(page_urls)} pages)")
                    
                # delay to be polite
                if completed % 5 == 0:
                    time.sleep(0.05)
                    
            except Exception as e:
                print(f"Failed to scrape {url}: {str(e)[:200]}")

    if DEBUG:
        print(f"\nTotal films found: {len(films)}")
    
    # scraping film details
    film_details = {}
    total_films = len(films)
    
    if films:
        detail_func = functools.partial(get_film_details, session=SESSION)
        
        # process all film details in parallel
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = {executor.submit(detail_func, film['film_slug']): film['film_slug'] for film in films}
            
            completed = 0
            batch_size = 25
            
            for future in as_completed(futures):
                slug = futures[future]
                try:
                    _, details = future.result()
                    film_details[slug] = details
                    completed += 1
                    
                    # progress reporting without significant delays
                    if DEBUG and completed % batch_size == 0:
                        title = next((f['title'] for f in films if f['film_slug'] == slug), "Unknown")
                        print(f"Processed {completed}/{total_films}: {title[:30]}...")
                        
                        # delay every few batches
                        if completed % (batch_size * 4) == 0:
                            time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Failed to process {slug}: {str(e)[:200]}")
    
    # combine results
    final_data = []
    for film in films:
        slug = film['film_slug']
        details = film_details.get(slug, {})
        final_data.append({**film, **details})
    
    return final_data
