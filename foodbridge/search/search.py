import re
from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from bs4 import BeautifulSoup
from .driver import Driver
import time

driver = Driver().driver

def getArticleIds():
    base_id = "r1-"
    article_ids = []
    for i in range(3):
        article_ids.append(base_id + str(i))
    return article_ids

def searchDDG(query):
    driver.get("https://duckduckgo.com/")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(2)
    
    article_ids = getArticleIds()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = []
    count = 0
    for article_id in article_ids:
        if len(links) == 3: break
        count += 1
        article = soup.find('article', id=article_id)
        if article:
            divs = article.find_all('div', recursive=False)
            if len(divs) >= 3:
                third_div = divs[2]
                link = third_div.find('a')['href']
                links.append(link)
    return links

def getClicableElements() -> Tuple[List[WebElement], List[str]]:
    # Find all clickable elements (links, buttons, and form-submit inputs)
    clickables = driver.find_elements(By.XPATH, 
        "//a | //button | //input[@type='button' or @type='submit' or @type='reset']")
    clickable_texts = [element.text for element in clickables]

    return clickables, clickable_texts

def getContent():
    # Find all content elements (paragraphs, headings, divs, etc.)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    content = soup.find_all("p")

    print(f"Found {len(content)} content elements.")
    text_content = []
    for element in content:
        try:
            text = clean_text(element.text)
            if len(text):
                text_content.append(text)
        except:
            pass
    return text_content

def getWebContent(url:str = "") -> Tuple[List[str], List[str], List[WebElement]]:
    if len(url):
        driver.get(url)
        time.sleep(2)
    (clickableElements, clickableTexts) = getClicableElements()
    return getContent(), clickableTexts, clickableElements

def clickElement(element:WebElement):
    element.click()
    time.sleep(2)
    return

def goBack():
    driver.back()
    time.sleep(2)
    return

def clean_text(text):
    """
    Cleans the input text by:
    1. Removing HTML/XML tags.
    2. Normalizing whitespaces (replacing multiple spaces, tabs, and newlines with a single space).
    3. Stripping leading and trailing whitespaces.
    """
    # Remove HTML/XML tags using regex
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespaces: replace multiple spaces, tabs, and newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading and trailing whitespaces
    text = text.strip()
    
    return text