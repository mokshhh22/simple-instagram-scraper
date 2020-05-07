import sys
import time
import string
import requests
import io
import re
import csv
from lxml import html
from bs4 import BeautifulSoup
 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


# Function to parse instagram account (Followers, Following, Posts)
# arguments - handle (username)
def parse_account(handle):
    url = "https://www.instagram.com/"
    try:
        page = requests.get(url+handle).text
        soup = BeautifulSoup(page, features="html.parser")
        string = soup.find("meta",  property="og:description")['content']

        followers = string.split(" Followers, ")[0].replace(",","").replace("k", "000")
        if "." in followers:
            followers = followers.replace(".","")[:-1]

        following = string.split(" Followers, ")[1].split(" Following, ")[0].replace(",","").replace("k", "000")
        if "." in following:
            following = following.replace(".","")[:-1]

        posts = string.split(" Followers, ")[1].split(" Following, ")[1].split(" Posts")[0].replace(",","").replace("k", "000")
        if "." in posts:
            posts = posts.replace(".","")[:-1]

        return { "followers": followers, "following": following, "posts": posts}
    except:
        return False


# Function to scrape public instagram post
def openInstagramPage(page_url):   
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path='./chromedriver')
    driver.get(page_url)
    # Wait to completely load the page
    time.sleep(3)

    # Remove login banner to maintian page structure
    if driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div/div/button'):
        driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div/div/button').click()

    # For loading more comments
    hasLoadMore = True
    while hasLoadMore:
        time.sleep(2)
        try:
            if driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/div/ul/li/div/button'):
                driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/article/div[2]/div/ul/li/div/button').click()
        except:
            hasLoadMore=False


    # Get all users comments
    users_list = []
    users = driver.find_elements_by_class_name('_6lAjh')

    for user in users:
        users_list.append(user.text)
    
    texts_list = []
    texts = driver.find_elements_by_class_name('C4VMK')
       
    for txt in texts:
        texts_list.append(txt.find_element_by_tag_name("span").text)
    

    results = []
    comments_count = len(users_list)

    for i in range(1, comments_count):
        user = users_list[i]
        text = texts_list[i]

        result = [user, text]
        results.append(result)
    
    with open('output.csv', mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(results)

    return results

if __name__ == "__main__":
    response = openInstagramPage(sys.argv[1].strip())
    print(response)