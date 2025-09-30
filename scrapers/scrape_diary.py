import requests
from bs4 import BeautifulSoup
import csv
import time

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

def get_diary_entries(username):
    base_url = f"https://letterboxd.com/{username}/films/diary/page/{{}}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    all_entries = []
    page = 1

    while True:
        print(f"Scraping page {page}...")
        response = requests.get(base_url.format(page), headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr', class_='diary-entry-row')

        if not rows:
            print("No more entries found.")
            break

        # track current month and year for entries that don't have them explicitly
        current_month = None
        current_year = None

        for row in rows:
            # extract film slug from the react component data
            react_component = row.find('div', class_='react-component')
            film_slug = None
            if react_component and 'data-item-slug' in react_component.attrs:
                film_slug = react_component['data-item-slug']
            
            # alternative: extract from data-postered-identifier
            if not film_slug:
                poster_div = row.find('div', class_='poster')
                if poster_div and poster_div.find('a'):
                    film_link = poster_div.find('a')['href']
                    # Extract film slug from film link (more generic approach)
                    if '/film/' in film_link:
                        film_slug = film_link.split('/film/')[-1].strip('/')

            # film name
            name_h2 = row.find('h2', class_='name')
            if name_h2:
                film_name_link = name_h2.find('a')
                film_name = film_name_link.get_text(strip=True) if film_name_link else None
            else:
                film_name = None

            # check if this row has month/year information (first entry of the month)
            month_link = row.find('a', class_='month')
            year_link = row.find('a', class_='year')
            day_link = row.find('a', class_='daydate')
            
            # update current month/year if this row has them
            if month_link and year_link:
                current_month = month_link.get_text(strip=True)
                current_year = year_link.get_text(strip=True)
            
            date = None
            if day_link and current_month and current_year:
                day = day_link.get_text(strip=True)
                date = f"{day} {current_month} {current_year}"

            rating = None
            rating_div = row.find('td', class_='col-rating')
            if rating_div:
                # look for the input field with the rating value
                rating_input = rating_div.find('input', class_='rateit-field')
                if rating_input and 'value' in rating_input.attrs:
                    # convert from 0-10 scale to 0-5 scale with half increments
                    rating_value = int(rating_input['value'])
                    if rating_value > 0:
                        rating = rating_value / 2.0

            # year
            year_td = row.find('td', class_='col-releaseyear')
            year = None
            if year_td:
                year_span = year_td.find('span')
                year = year_span.get_text(strip=True) if year_span else None

            # alternative year extraction from release date span
            if not year:
                release_span = row.find('span', class_='releasedate')
                if release_span:
                    year_link = release_span.find('a')
                    year = year_link.get_text(strip=True) if year_link else None

            all_entries.append({
                'name': film_name,
                'film_slug': film_slug,
                'date': date,
                'rating': rating,
                'year': year
            })

        page += 1
        time.sleep(1)

    return all_entries


# test the scraper
if __name__ == "__main__":
    username = "rubylu"
    
    print(f"Starting to scrape diary entries for {username}...")
    
    try:
        entries = get_diary_entries(username)
        
        print(f"Successfully scraped {len(entries)} entries!")
        
        entries_with_dates = sum(1 for entry in entries if entry['date'])
        print(f"Entries with dates: {entries_with_dates}/{len(entries)}")
        
        filename = f"{username}_diary_entries.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'film_slug', 'date', 'rating', 'year']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry)
        
        print(f"Data saved to {filename}")
                
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
