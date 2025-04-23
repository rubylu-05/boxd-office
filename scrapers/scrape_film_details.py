import requests
from bs4 import BeautifulSoup

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
        'cast': [],
        'studios': [],
        'countries': [],
        'language': None
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

        details_div = soup.find('div', id='tab-details')
        
        # get studios, countries, and primary language
        if details_div:
            details['studios'] = [a.text for a in details_div.find_all('a', href=lambda x: x and '/studio/' in x)]
            details['countries'] = [a.text for a in details_div.find_all('a', href=lambda x: x and '/films/country/' in x)]

            # extract just the primary language
            lang_header = details_div.find('h3', string=lambda text: text and "Primary Language" in text)
            if lang_header:
                lang_block = lang_header.find_next_sibling('div', class_='text-sluglist')
                if lang_block:
                    lang_link = lang_block.find('a')
                    if lang_link:
                        details['language'] = lang_link.text.strip()
                    else:
                        details['language'] = None
            else:
                # check for "Language" section if "Primary Language" isn't present
                lang_header = details_div.find('h3', string=lambda text: text and "Language" in text)
                if lang_header:
                    lang_block = lang_header.find_next_sibling('div', class_='text-sluglist')
                    if lang_block:
                        lang_link = lang_block.find('a')
                        if lang_link:
                            details['language'] = lang_link.text.strip()
                        else:
                            details['language'] = None
                else:
                    details['language'] = None

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
