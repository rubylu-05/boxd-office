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

        # get cast
        actor_div = soup.find('div', id='tab-cast')
        if actor_div:
            details['cast'] = [a.text.strip() for a in actor_div.find_all('a', href=lambda x: x and '/actor/' in x)[:12]]

        # get language
        lang_header = soup.find('h3', string=lambda t: t and 'Language' in t)
        if lang_header:
            lang_link = lang_header.find_next_sibling('div').find('a')
            details['language'] = lang_link.text.strip() if lang_link else None

        try:
            # get ratings
            ratings_url = f"https://letterboxd.com/csi/film/{film_slug}/rating-histogram/"
            ratings_response = session.get(ratings_url, timeout=10)
            if ratings_response.status_code == 200:
                rating_tag = BeautifulSoup(ratings_response.text, 'html.parser').find('a', class_='display-rating')
                if rating_tag and 'title' in rating_tag.attrs:
                    try:
                        details['avg_rating'] = float(rating_tag['title'].split("Weighted average of ")[1].split(" based")[0])
                    except (IndexError, ValueError):
                        pass

            # get stats
            stats_url = f"https://letterboxd.com/csi/film/{film_slug}/stats/"
            stats_response = session.get(stats_url, timeout=10)
            if stats_response.status_code == 200:
                stats_soup = BeautifulSoup(stats_response.text, 'html.parser')
                watched = stats_soup.find('a', class_='icon-watched')
                liked = stats_soup.find('a', class_='icon-liked')
                details['num_watched'] = get_digits(watched['title']) if watched and 'title' in watched.attrs else None
                details['num_liked'] = get_digits(liked['title']) if liked and 'title' in liked.attrs else None

            # small delay between api calls
            time.sleep(0.1 + random.random() * 0.5)
        except Exception:
            pass

    except Exception as e:
        return film_slug, details

    return film_slug, details