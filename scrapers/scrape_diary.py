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

base_url = "https://letterboxd.com/rubylu/films/diary/page/{}/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

all_entries = []
page = 1

while True:
    response = requests.get(base_url.format(page), headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr', class_='diary-entry-row')

    if not rows:
        break

    # track current month and year for date rows without td-calendar
    current_month = None
    current_year = None

    for row in rows:
        film_poster_div = row.find('div', class_='film-poster')
        film_slug = film_poster_div['data-film-slug'] if film_poster_div else None

        # film name
        name_h3 = row.find('h3', class_='headline-3 prettify')
        film_name = name_h3.find('a').get_text(strip=True) if name_h3 else None

        # date
        day_td = row.find('td', class_='td-day')
        month_year_div = row.find('td', class_='td-calendar')

        if month_year_div:
            month_tag = month_year_div.find('strong')
            year_tag = month_year_div.find('small')
            if month_tag and year_tag:
                current_month = month_tag.get_text(strip=True)
                current_year = year_tag.get_text(strip=True)

        if day_td and current_month and current_year:
            day = day_td.get_text(strip=True)
            date = f"{day} {current_month} {current_year}"
        else:
            date = None

        # rating
        rating_td = row.find('td', class_='td-rating')
        if rating_td:
            star_span = rating_td.find('span', class_='rating')
            star_str = star_span.get_text(strip=True) if star_span else None
            rating = star_to_rating.get(star_str, None)
        else:
            rating = None

        all_entries.append({
            'name': film_name,
            'film_slug': film_slug,
            'date': date,
            'rating': rating
        })

    page += 1

df = pd.DataFrame(all_entries)
df.to_csv('rubylu_diary.csv', index=False)
