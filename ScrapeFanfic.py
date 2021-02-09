from fanfiction import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from selenium import webdriver
import time, re, requests
from bs4 import BeautifulSoup
import pickle

def get_n_stories(medium, base_url, n):
    url = base_url + medium
    print(f'Scraping {url} page.')

    wd = webdriver.Chrome()
    wd.get(url)
    page_source = wd.page_source
    wd.close()

    soup = BeautifulSoup(page_source, "lxml")
    stories = soup.find("div", {"id": "list_output"})

    story_urls = []
    for story in stories.find_all('a', href=True)[0:n]:
        story_urls.append(story['href'])

    return story_urls

def get_n_works(story_url, base_url, n):
    # sort by most reviewed
    url = base_url + story_url + '?&srt=4&r=103'
    print(f'Scraping {url} page.')

    wd = webdriver.Chrome()
    wd.get(url)
    page_source = wd.page_source
    wd.close()

    soup = BeautifulSoup(page_source, "lxml")

    work_urls = []
    for story in soup.find_all("a", class_="stitle")[0:n]:
        p = re.compile(u"(?<=/s/)(.*)(?=/1/)")
        result = p.search(story['href'])
        work_urls.append(result.group(1))

    return work_urls

scraper = Scraper()
base_url = 'https://www.fanfiction.net/'
mediums = ['anime', 'book', 'cartoon', 'movie', 'tv']
data = []
error_ids = []

# iterate over mediums
for medium in mediums:
    print(f'Scraping {medium} medium.')

    # get top N stories (fictional universes) within the medium
    story_urls = get_n_stories(medium, base_url, 5)
    print(story_urls)

    time.sleep(1)

    for story_url in tqdm(story_urls):

        # get top N works with the story (fictional universe)
        story_ids = get_n_works(story_url, base_url, n = 25)
        print(story_ids)

        time.sleep(1)
        for id in tqdm(story_ids):
            print(f'Scraping {id} work.')

            try:
                # get the first N chapters of the story.
                metadata = scraper.scrape_n_chapters(id, n = 3)
                data.append(metadata)
            except:
                print(f'error with story number {id}')
                error_ids.append(id)

            pickle.dump(data, open("data.pickle", "wb"))

            time.sleep(1)

    print(error_ids)

pickle.dump(data, open("data_done.pickle", "wb"))
print(data)
print(error_ids)