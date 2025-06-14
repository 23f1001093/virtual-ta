import os, time, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

BASE_URL = "https://tds.s-anand.net/#/"
OUTPUT_FILE = "data/course_notes.json"

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def scrape():
    driver = setup_driver()
    driver.get(BASE_URL)
    time.sleep(5)
    sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
    links = sidebar.find_elements(By.TAG_NAME, "a")
    
    chapters = []
    for a in links:
        href = a.get_attribute("href")
        title = a.text.strip()
        if not title or "README" in href:
            continue
        driver.get(href)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        h1 = soup.select_one("h1, h2")
        items = [li.text.strip() for li in soup.select("li") if li.text.strip()]
        chapters.append({
            "section": h1.text.strip() if h1 else title,
            "url": href,
            "points": items
        })

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(chapters, f, indent=2)
    print(f"✅ Saved to {OUTPUT_FILE}")
    driver.quit()

if __name__ == "__main__":
    scrape()
