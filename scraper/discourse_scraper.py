from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("DISCOURSE_EMAIL")
PASSWORD = os.getenv("DISCOURSE_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("❌ DISCOURSE_EMAIL or DISCOURSE_PASSWORD is missing. Check your .env file.")

LOGIN_URL = "https://discourse.onlinedegree.iitm.ac.in/login"
CATEGORY_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"

def setup_driver():
    options = Options()
    options.headless = False
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def login(driver):
    driver.get(LOGIN_URL)
    time.sleep(2)

    email_input = driver.find_element(By.ID, "login-account-name")
    email_input.send_keys(EMAIL)
    password_input = driver.find_element(By.ID, "login-account-password")
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)

    time.sleep(5)

def get_discourse_posts(driver):
    driver.get(CATEGORY_URL)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    topics = []
    for a_tag in soup.select("a.title"):
        href = a_tag.get("href")
        title = a_tag.get_text(strip=True)
        if href and href.startswith("/t/"):
            full_url = "https://discourse.onlinedegree.iitm.ac.in" + href
            topics.append({"title": title, "url": full_url})

    results = []
    for topic in topics:
        driver.get(topic["url"])
        time.sleep(2)
        post_soup = BeautifulSoup(driver.page_source, 'html.parser')
        posts = post_soup.select("div.cooked")
        results.append({
            "title": topic["title"],
            "url": topic["url"],
            "posts": [
                {"content": p.get_text(separator="\n", strip=True)} for p in posts
            ]
        })

    return results

def scrape_discourse():
    driver = setup_driver()
    login(driver)
    posts = get_discourse_posts(driver)
    driver.quit()

    os.makedirs("data", exist_ok=True)
    with open("data/discourse_posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    print(f"✅ Scraped {len(posts)} posts.")

if __name__ == "__main__":
    scrape_discourse()
