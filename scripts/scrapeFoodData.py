import os
import time
from typing import Tuple
from foodbridge.vectorDb.FoodDb import FoodDb 
from foodbridge.search.driver import Driver
from selenium.webdriver.common.by import By

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Base URL for the USDA FoodData Central website
BASE_URL = "https://fdc.nal.usda.gov"

# URL for the food search page
SEARCH_URL = "https://fdc.nal.usda.gov/food-search?type=Survey%20(FNDDS)&marketCountries=United%20States,Canada,New%20Zealand"
DRIVER = Driver().driver

KEY_CSV = "food_data.csv"
PAIR_CSV = "food_pair.csv"

def get_page_number(text_content:str) -> Tuple[int, int]:
    match = re.search(r"Currently showing page (\d+) of (\d+) total pages", text_content)
    if match:
        current_page = int(match.group(1))
        total_pages = int(match.group(2))
        return current_page, total_pages
    return -1, -1

# Function to scrape food names and their detail page URLs
def scrape_food_list():

    food_data = {}
    DRIVER.get(SEARCH_URL)
    time.sleep(2)

    soup = BeautifulSoup(DRIVER.page_source, "html.parser")

    div_exact = soup.find('div', class_="page-number")
    current_page, total_pages = get_page_number(div_exact.text) #type: ignore

    while(current_page != total_pages):
        # Find the table with class "usa-table-results"
        table = soup.find("table", class_="usa-table-results")
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells: continue
            food_cell = cells[1]
            anchor_tag = food_cell.find("a")
            food_name = anchor_tag.text
            food_url = BASE_URL + anchor_tag["href"]
            food_data[food_name] = food_url
            append_to_csv({"food_name": food_name, "url": food_url, "page_number": current_page}, KEY_CSV)
        
        DRIVER.find_element(By.LINK_TEXT, str(current_page+1)).click()
        time.sleep(2)
        soup = BeautifulSoup(DRIVER.page_source, "html.parser")
        div_exact = soup.find('div', class_="page-number")
        current_page, total_pages = get_page_number(div_exact.text) #type: ignore

    return food_data

# Function to scrape detailed data for a specific food
def scrape_food_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the table data
    table = soup.find("table", class_="nutrient-table")
    if not table:
        return {}

    # Parse the table rows
    details = {}
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            key = cells[0].text.strip()
            value = cells[1].text.strip()
            details[key] = value

    return details

# Main function to scrape all food data
def scrape_all_food_data():
    food_list = scrape_food_list()
    all_food_data = []

    for food in food_list:
        print(f"Scraping data for: {food['food_name']}")
        details = scrape_food_details(food["url"])
        food_data = {"food_name": food["food_name"], **details}
        all_food_data.append(food_data)

    return all_food_data

# Save the data to a CSV file
def save_to_csv(data, filename="food_data.csv"):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def append_to_csv(data, filename):
    # Convert data to a DataFrame
    df = pd.DataFrame([data])

    # Check if the file exists
    if not os.path.isfile(filename):
        # Create a new file with headers
        df.to_csv(filename, index=False)
    else:
        # Append to the existing file without headers
        df.to_csv(filename, mode="a", header=False, index=False)

def scrapeIndividual():
    keys = pd.read_csv(KEY_CSV)
    keys = keys.iloc[2766:]
    for index, row in keys.iterrows():
        food_name = row["food_name"] 
        url = row["url"]
        DRIVER.get(url)
        time.sleep(0.5)
        soup = BeautifulSoup(DRIVER.page_source, "html.parser")
        try:
            table = soup.find("table", id="nutrients-table")
            rows = table.find_all("tr")
            prev = ""

            for row in rows:
                cells = row.find_all("td")
                if not cells or len(cells) < 3: continue
                component = cells[0].text
                amount = cells[1].text
                unit = cells[2].text
                content = f"{prev}|food component: {component} amount: {amount} unit: {unit}|"
                prev = content
            append_to_csv({"food_name": food_name, "content": prev}, PAIR_CSV)
        except:
            print(f"Error in scraping {food_name}")
            continue

def insert_into_db():
    food_data = pd.read_csv(PAIR_CSV)
    food_db = FoodDb()
    for index, row in food_data.iterrows():
        food_name = row["food_name"]
        content = row["nutrition_info"]
        try:
            food_db.add(food_name, food_name)
        except:
            print(f"Error in adding {food_name} {content}")
            continue
    print("successfully added to db")

def testDb():
    food_db = FoodDb()
    results = food_db.search_similar_foods("Summer squash, yellow or green, frozen, cooked with butter or margarine")
    print(results)

testDb()