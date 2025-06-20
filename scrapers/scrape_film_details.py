from bs4 import BeautifulSoup
import time
import random
import re

def get_digits(text):
    if not text:
        return None
    try:
        return int(''.join(c for c in text if c.isdigit()))
    except (ValueError, TypeError):
        return None

def parse_stat_number(text):
    # convert numbers like '2.1M' or '327K' to integers
    if not text:
        return None
    text = text.strip()
    multiplier = 1
    if 'K' in text:
        multiplier = 1000
        text = text.replace('K', '')
    elif 'M' in text:
        multiplier = 1000000
        text = text.replace('M', '')
    
    try:
        if '.' in text:
            return int(float(text) * multiplier)
        return int(text) * multiplier
    except (ValueError, TypeError):
        return None

def get_film_details(film_slug, session):
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
        response = session.get(film_url, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"Status {response.status_code} for {film_url}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # get year
        production_section = soup.find('section', class_='production-masthead')
        if production_section:
            releaseyear_div = production_section.find('div', class_='releaseyear')
            if releaseyear_div:
                year_link = releaseyear_div.find('a')
                if year_link:
                    details['year'] = year_link.text.strip()
        if not details['year']:
            release_year = soup.find('meta', {'property': 'og:title'})
            if release_year and 'content' in release_year.attrs:
                year_match = re.search(r'\((\d{4})\)', release_year['content'])
                if year_match:
                    details['year'] = year_match.group(1)

        # get runtime
        runtime_tag = soup.find('p', class_='text-link')
        if runtime_tag:
            details['runtime'] = get_digits(runtime_tag.get_text(strip=True))

        # get genres and themes
        genre_div = soup.find('div', id='tab-genres')
        if genre_div:
            details['genres'] = [a.text.strip() for a in genre_div.find_all('a', href=lambda x: x and '/films/genre/' in x)]
            details['themes'] = [a.text.strip() for a in genre_div.find_all('a', href=lambda x: x and ('/films/theme/' in x or '/films/mini-theme/' in x))]

        # get directors
        director_div = soup.find('div', id='tab-crew')
        if director_div:
            details['directors'] = [a.text.strip() for a in director_div.find_all('a', href=lambda x: x and '/director/' in x)]

        # get cast (first 12)
        actor_div = soup.find('div', id='tab-cast')
        if actor_div:
            details['cast'] = [a.text.strip() for a in actor_div.find_all('a', href=lambda x: x and '/actor/' in x)[:12]]

        details_div = soup.find('div', id='tab-details')
        if details_div:
            # get studios
            studio_links = details_div.find_all('a', href=lambda x: x and '/studio/' in x)
            details['studios'] = [link.text.strip() for link in studio_links]
            
            # get countries
            country_links = details_div.find_all('a', href=lambda x: x and '/films/country/' in x)
            details['countries'] = [link.text.strip() for link in country_links]

            # get language
            lang_header = details_div.find('h3', string=lambda t: t and ('Language' in t or 'Primary Language' in t))
            if lang_header:
                lang_block = lang_header.find_next_sibling('div')
                if lang_block:
                    lang_link = lang_block.find('a')
                    details['language'] = lang_link.text.strip() if lang_link else None

        # get number of members watched and liked
        stats_url = f"https://letterboxd.com/csi/film/{film_slug}/stats/"
        stats_response = session.get(stats_url, timeout=10)
        if stats_response.status_code == 200:
            stats_soup = BeautifulSoup(stats_response.text, 'html.parser')
            stats_text = stats_soup.get_text().split()
            if len(stats_text) >= 3:
                details['num_watched'] = parse_stat_number(stats_text[0])
                details['num_liked'] = parse_stat_number(stats_text[2])

        # get average rating
        ratings_url = f"https://letterboxd.com/csi/film/{film_slug}/ratings-summary/"
        ratings_response = session.get(ratings_url, timeout=10)
        if ratings_response.status_code == 200:
            ratings_soup = BeautifulSoup(ratings_response.text, 'html.parser')
            ratings_text = ratings_soup.get_text()
            match = re.search(r'(\d+\.\d+)\s+★', ratings_text)
            if match:
                average_rating = match.group(1)
                details['avg_rating'] = float(average_rating)

        # small delay between api calls
        time.sleep(0.1 + random.random() * 0.5)

    except Exception as e:
        print(f"Error processing {film_slug}: {str(e)}")
        return film_slug, details

    return film_slug, details