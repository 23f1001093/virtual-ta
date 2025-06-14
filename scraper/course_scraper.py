import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

BASE_URL = "https://tds.s-anand.net/#/"
OUTPUT_FILE = "data/course_notes.json"


def setup_driver():
    options = Options()
    options.add_argument("--headless")  # Change to False to debug visually
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


def expand_sidebar(driver):
    print("📂 Expanding all sidebar sections...")
    sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
    buttons = sidebar.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        try:
            btn.click()
            time.sleep(0.3)
        except:
            continue


def get_sidebar_links(driver):
    print("🔗 Extracting all chapter links...")
    sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
    a_tags = sidebar.find_elements(By.TAG_NAME, "a")

    links = []
    for a in a_tags:
        href = a.get_attribute("href")
        text = a.text.strip()
        if href and text and href.startswith(BASE_URL) and "README" not in href:
            links.append({"title": text, "url": href})
    print(f"✅ Found {len(links)} links.")
    return links


def extract_youtube_links(soup):
    return [iframe.get("src") for iframe in soup.find_all("iframe") if "youtube" in iframe.get("src", "")]


def scrape_chapter(driver, url):
    driver.get(url)
    time.sleep(1.5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    header = soup.select_one("h1, h2")
    section_title = header.get_text(strip=True) if header else "Untitled"

    bullets = [li.get_text(strip=True) for li in soup.select("li") if li.get_text(strip=True)]
    yt_links = extract_youtube_links(soup)

    return {
        "section": section_title,
        "url": url,
        "points": bullets,
        "videos": yt_links
    }


def scrape_course():
    driver = setup_driver()
    print("📘 Opening base course page...")
    driver.get(BASE_URL)
    time.sleep(3)

    expand_sidebar(driver)
    chapters = get_sidebar_links(driver)

    results = []
    for ch in chapters:
        print(f"→ Scraping: {ch['title']}")
        try:
            data = scrape_chapter(driver, ch["url"])
            results.append(data)
        except Exception as e:
            print(f"❌ Error scraping {ch['title']}: {e}")

    driver.quit()

    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(results)} chapters to {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_course()
