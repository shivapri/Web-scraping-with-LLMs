import json
import time
import random
from datetime import datetime
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import os

# Rest of the imports and USER_AGENTS remain the same

# Setup and parse_date functions remain the same
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    # Add more user-agents as needed
]

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'user-agent={random.choice(USER_AGENTS)}')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def parse_date(date_str):
    try:
        return parser.parse(date_str)
    except Exception as e:
        print(f"Parsing failed: {e}")
        return None
def save_to_csv(articles, csv_file):
    """Helper function to save articles to CSV"""
    file_exists = os.path.isfile(csv_file)
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['article_title', 'published_date', 'article_content', 'location', 'source_url'])
        
        # Write the header only if the file doesn't already exist
        if not file_exists:
            writer.writeheader()
        
        # Write the articles to the CSV file
        writer.writerows(articles)
    
    print(f"Saved {len(articles)} articles to {csv_file}")

def scrape_website(url, region="United States", start_page=1, max_pages=2, max_articles=None):
    driver = setup_driver()
    articles = []
    csv_file = "data/articles_news-releases-list_businesswire.csv"
    existing_urls = set()

    if os.path.isfile(csv_file):
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            print("Reading the csv file")
            reader = csv.DictReader(f)
            for row in reader:
                if 'source_url' in row and row['source_url']:
                    existing_urls.add(row['source_url'])
        print(f"Found {len(existing_urls)} existing articles in the CSV")
    else:
        print("No existing file, scraping for the first time.")
    
    try:
        driver.get(url)
        time.sleep(random.uniform(3, 7))  # Random delay to mimic human behavior

        # # Set the date to January 1, 2025
        # date_input = driver.find_element(By.ID, "date")
        # date_input.clear()
        # date_input.send_keys("04/15/2025")
        # time.sleep(1)

        # # Click the "Go" button
        # go_button = driver.find_element(By.ID, "GoButton")
        # go_button.click()
        # time.sleep(random.uniform(3, 7))

        # Navigate to the start page if needed
        page_number = 1
        while page_number < start_page:
            print(f"Skipping to page {page_number + 1}")
            next_button_clicked = driver.execute_script("""
                const nextBtn = document.querySelector("ul.pagination a[aria-label='Next']");
                if (nextBtn && !nextBtn.hasAttribute('disabled') && !nextBtn.parentElement.classList.contains('disabled')) {
                    nextBtn.click();
                    return true;
                }
                return false;
            """)
            
            if next_button_clicked:
                page_number += 1
                time.sleep(random.uniform(3, 5))
            else:
                print("Could not navigate to the requested start page. Starting from the current page.")
                break
        
        has_next_page = True
        all_article_links = []
        
        # First pass: collect all article links from pages
        while has_next_page and page_number <= max_pages:
            print(f"Collecting links from page {page_number}")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all cards on the current page using the updated selector
            cards = soup.select('.relative')
            print(f"Found {len(cards)} cards on page {page_number}")
            
            for item in cards:
                # Extract link using the updated structure
                link_elem = item.select_one('a.font-figtree')
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                
                if not link:
                    continue
                    
                # Check if the link is relative and prepend the domain if needed
                if link and not link.startswith(('http://', 'https://')):
                    link = f"https://www.businesswire.com{link if link.startswith('/') else '/' + link}"
                
                # Extract date using the updated structure
                date_elem = item.select_one('.flex.flex-wrap.items-center.gap-2 span')
                date_str = date_elem.text.strip() if date_elem else ""
                date = parse_date(date_str) if date_str else None
                
                # Extract title using the updated structure
                title_elem = item.select_one('h2.text-primary')
                title = title_elem.text.strip() if title_elem else ""
                
                # Extract mini description
                description_elem = item.select_one('.rich-text')
                description = description_elem.text.strip() if description_elem else ""
                
                # Only add links that meet our date criteria and haven't been scraped before
                if link and date and date >= datetime(2025, 1, 1) and link not in existing_urls:
                    all_article_links.append({
                        'link': link,
                        'title': title,
                        'date_str': date_str,
                        'description': description
                    })
                    print(f"Added link to queue: {link}")
            
            # Check if we've collected enough articles
            if max_articles and len(all_article_links) >= max_articles:
                print(f"Reached maximum number of articles to collect: {max_articles}")
                break
            
            # Navigate to the next page if available
            page_number += 1
            
            try:
                next_button_clicked = driver.execute_script("""
                    const buttons = document.querySelectorAll('button.text-primary.font-semibold, button.flex.items-center.justify-center.gap-2.text-sm.text-primary.font-semibold');
                    for (let btn of buttons) {
                        if (btn.textContent.includes('Next')) {
                            if (!btn.disabled && !btn.classList.contains('opacity-0') && !btn.classList.contains('pointer-events-none')) {
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                """)
                
                if next_button_clicked:
                    print(f"Clicked next button, moving to page {page_number}")
                    time.sleep(random.uniform(3, 5))
                else:
                    print("No more pages available or next button is disabled")
                    has_next_page = False
                
            except Exception as e:
                print(f"Error during pagination: {e}")
                has_next_page = False
        
        # Process each article detail page
        print(f"Collected {len(all_article_links)} unique article links to process")
        
        for i, article_data in enumerate(all_article_links):
            if max_articles and i >= max_articles:
                break
                
            link = article_data['link']
            print(f"Processing article {i+1}/{len(all_article_links)}: {link}")
            
            try:
                driver.get(link)
                time.sleep(random.uniform(2, 5))
                
                # Extract full content
                detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                full_content_elem = detail_soup.select_one('.ui-kit-press-release__content')
                full_content = full_content_elem.text.strip() if full_content_elem else ""
                
                # Add to articles list
                articles.append({
                    'article_title': article_data['title'],
                    'published_date': article_data['date_str'],
                    'article_content': full_content,
                    'location': "",
                    'source_url': link
                })
                
                # Periodically save results
                if (i + 1) % 10 == 0:
                    print(f"Saving batch of articles ({i+1} processed so far)")
                    save_to_csv(articles, csv_file)
                    articles = []
                
                time.sleep(random.uniform(3, 7))
                
            except Exception as e:
                print(f"Error processing article {link}: {e}")
        
        # Save any remaining articles
        if articles:
            save_to_csv(articles, csv_file)
            
    finally:
        driver.quit()
    
    return articles

if __name__ == "__main__":
    websites = [
    #   "https://www.businesswire.com/newsroom",
    #   "https://www.businesswire.com/newsroom?keywords=ENTIRE_RELEASE%3Atrue%3ACTO%7CENTIRE_RELEASE%3Atrue%3ACEO&language=en&region=1000337%7C1000400%7C1005845&industry=1000178",
    "https://www.businesswire.com/newsroom?keywords=ENTIRE_RELEASE%3Atrue%3ACTO%7CENTIRE_RELEASE%3Atrue%3ACEO%7CENTIRE_RELEASE%3Atrue%3ACFO&language=en&region=1000400&industry=1000178&subject=1778691%7C1778692%7C1778694%7C1000006%7C1000011%7C1000015%7C1778693",
        # Add more URLs here
    ]
    
    # Set parameters
    start_page = 1  # Change to start from a specific page
    max_pages = 20   # Maximum number of pages to scrape
    max_articles = 150  # Maximum number of articles to scrape, set to None for unlimited
    
    for url in websites[:1]:  # Limit to 1 for testing; remove slice for all
        scrape_website(url, region="United States", start_page=start_page, max_pages=max_pages, max_articles=max_articles)
        time.sleep(random.uniform(5, 10))  # Delay between sites
