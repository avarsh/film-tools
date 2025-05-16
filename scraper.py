from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
from os import path
import stats
import math

# Global constants
STAR_CHR = "★"
HALF_CHR = "½"

'''
Retrieve webpage HTML.
'''
def get_soup(url):
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
    page = urllib.request.urlopen( req )

    html = page.read().decode("utf-8")
    return BeautifulSoup(html, "html.parser")

'''
Retrieve webpage, running all scripts and optionally waiting on an element to load.
'''
def get_dynamic_soup(browser, url, wait_on_elem=None):
    browser.get(url)
    # Sometimes the page might take some time to run all the scripts,
    # so we wait up to 5 seconds.
    if wait_on_elem != None:
        timeout = 5
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, wait_on_elem))
            WebDriverWait(browser, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")
            return None

    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    return soup

'''
Retrieve a user's reviews page.
'''
def get_user_reviews_page(lb_user, page_num=1):
    url = f"https://letterboxd.com/{lb_user}/films/page/{page_num}/"
    return get_soup(url)

'''
Get number of pages of reviews for a user.
'''
def get_num_pages(soup):
    page_counter = soup.find("div", {"class": "paginate-pages"})
    if page_counter:
        return int(page_counter.findChildren()[0].findChildren("li")[-1].text)
    
    return 1

'''
Given a page of a user's movie reviews, find all ratings.
'''
def get_movie_reviews(soup):
    containers = soup.find_all("li", {"class": "poster-container"})
    
    movies = []
    for movie in containers:
        poster = movie.find("div", {"class": "poster"})
        link = poster["data-target-link"]

        viewing_data = movie.find("p", {"class" : "poster-viewingdata"})
        rating = viewing_data.text.strip()

        if rating and (rating[0] == STAR_CHR or rating[0] == HALF_CHR):
            total = rating.count("★")
            if rating[-1] == HALF_CHR:
                total += 0.5
            movies.append((link, total))

    return movies


def get_movie_stats(browser, link):
    url = "https://letterboxd.com" + link
    print(url)
    soup = get_dynamic_soup(browser, url, "ratings-histogram-chart")
    if soup == None:
        return 0, 0, [0] * 10

    histogram = soup.find({"class" : "ratings-histogram-chart"})
    bars = soup.find_all("li", {"class" : "rating-histogram-bar"})

    ratings = []
    for bar in bars:
        first_word = bar.find("a")
        if first_word == None:
            first_word = bar
        
        first_word = first_word["data-original-title"].split()[0]

        if first_word == "No":
            ratings.append(0)
        else:
            ratings.append(int(first_word.replace(",", "")))
    with open('data/movie-db.csv', 'a') as f:
        f.write(link + ", " + str(ratings) + "\n")

    average, variance = stats.compute_stats(ratings)

    std_dev = math.sqrt(variance)

    return average, std_dev, ratings

def create_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox") 
    browser = webdriver.Chrome(options=options)
    return browser



def get_user_reviews(user):
    user_data_file = f"data/users/{user}.csv"

    if path.isfile(user_data_file):
        with open(user_data_file, 'r') as f:
            lines = f.readlines()
            reviews = []
            for r in lines:
                r = r.split(',')
                movie = r[0]
                score = float(r[1].strip())
                reviews.append((movie, score))
    else:
        soup = get_user_reviews_page(user)
        num_pages = get_num_pages(soup)
        reviews = []
        for i in range(1, num_pages + 1):
            page = get_user_reviews_page(user, i)
            reviews += get_movie_reviews(page)

            with open(user_data_file, "w") as f:
                for movie in reviews:
                    f.write(movie[0] + ", " + str(movie[1]) + "\n")

    print("Obtained user reviews for", user)
    return reviews
