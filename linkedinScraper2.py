from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import re

# 🔐 LinkedIn credentials
USERNAME = "anesh@fiveoak.com"
PASSWORD = "Zlatan@123"

# 🔗 List of LinkedIn profile URLs to scrape
PROFILE_URLS = [
    "http://www.linkedin.com/in/jo-steinberg-5214131",
    "http://www.linkedin.com/in/mariana-romo-78557a78",
    "http://www.linkedin.com/in/crystal-andre-smith-b93801128",
    "http://www.linkedin.com/in/katelyn-mccormack-80162448",
    "http://www.linkedin.com/in/michelle-johnson-5a2455154"
]

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(options=options)

def login_linkedin(driver, username, password):
    driver.get("https://www.linkedin.com/login")
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        time.sleep(5)
    except Exception as e:
        print(f"❌ Login failed: {e}")
        driver.quit()
        exit()

def detect_linkedin_company_page(driver, soup):
    linkedin_page = "NO"
    original_window = driver.current_window_handle

    try:
        # === Primary: Look for current role in experience section ===
        exp_section = soup.find('section', {'id': re.compile(r'experience.*', re.IGNORECASE)})
        if exp_section:
            roles = exp_section.find_all('li')
            for role in roles:
                date_span = role.find('span', string=re.compile(r'Present', re.IGNORECASE))
                if date_span:
                    link = role.find('a', href=True)
                    if link and link['href'].startswith("https://www.linkedin.com/company/"):
                        href = link['href']
                        canonical_format = re.match(r"https://www\.linkedin\.com/company/[a-zA-Z0-9\-]+/?$", href)
                        if canonical_format:
                            linkedin_page = "YES"
                            print(f"✅ Found current company link: {href}")
                            return linkedin_page
                        else:
                            print(f"⚠️ Found link but not canonical: {href}")

        # === Fallback: Scan all links for any valid company page ===
        all_links = soup.find_all('a', href=True)
        print(f"🔍 Found {len(all_links)} total links on page")

        for link in all_links:
            href = link['href']
            if href.startswith("https://www.linkedin.com/company/") and \
               "admin" not in href and "inbox" not in href and "search/results/all" not in href:
                print(f"🔍 Found fallback company link: {href}")
                driver.execute_script("window.open(arguments[0]);", href)
                WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))

                for handle in driver.window_handles:
                    if handle != original_window:
                        driver.switch_to.window(handle)
                        break

                time.sleep(3)
                current_url = driver.current_url
                print(f"🔍 Opened fallback company URL: {current_url}")

                canonical_format = re.match(r"https://www\.linkedin\.com/company/[a-zA-Z0-9\-]+/?$", current_url)
                if canonical_format:
                    linkedin_page = "YES"
                else:
                    print("⚠️ Fallback URL is not canonical. Marking as NO.")

                driver.close()
                driver.switch_to.window(original_window)
                return linkedin_page

    except Exception as e:
        print(f"❌ Error detecting company page: {e}")
        linkedin_page = "NO"

    return linkedin_page

def scrape_profile(driver, url):
    driver.get(url)
    time.sleep(random.uniform(5, 8))  # Anti-bot delay
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # --- Extract Connections ---
    connection_text = "Not found"
    all_spans = soup.find_all('span')
    for span in all_spans:
        if span.text and 'connections' in span.text.lower():
            connection_text = span.text.strip()
            break

    # --- Extract Followers ---
    follower_text = "Not found"
    for span in all_spans:
        if span.text and 'followers' in span.text.lower():
            follower_text = span.text.strip()
            break

    # --- Extract Last Activity ---
    last_activity = "No public posts found"
    activity_type = "None"
    time_pattern = re.compile(r'\b(\d+\s?(w|d|mo|h|week|day|month|hour)s?)\b', re.IGNORECASE)
    posts = soup.find_all('div', class_='feed-shared-update-v2')
    for post in posts:
        spans = post.find_all('span')
        for span in spans:
            text = span.get_text(strip=True)
            if time_pattern.search(text):
                last_activity = time_pattern.search(text).group(1)
                activity_type = "posted"
                break
        if last_activity != "No public posts found":
            break

    if last_activity == "No public posts found":
        for span in all_spans:
            text = span.get_text(strip=True).lower()
            if 'commented on a post' in text and time_pattern.search(text):
                last_activity = time_pattern.search(text).group(1)
                activity_type = "commented"
                break
            elif 'reposted' in text and time_pattern.search(text):
                last_activity = time_pattern.search(text).group(1)
                activity_type = "reposted"
                break
            elif 'liked this post' in text and time_pattern.search(text):
                last_activity = time_pattern.search(text).group(1)
                activity_type = "liked"
                break

    # --- Detect LinkedIn company page ---
    linkedin_page = detect_linkedin_company_page(driver, soup)

    return {
        "url": url,
        "followers": follower_text,
        "connections": connection_text,
        "last_activity": last_activity,
        "activity_type": activity_type,
        "linkedinpage": linkedin_page
    }

def main():
    driver = setup_driver()
    login_linkedin(driver, USERNAME, PASSWORD)
    results = []
    for url in PROFILE_URLS:
        try:
            data = scrape_profile(driver, url)
            results.append(data)
            print(f"✅ Scraped: {url}")
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
    driver.quit()

    # Display results
    for r in results:
        print("\n---")
        print(f"🔗 Profile: {r['url']}")
        print(f"👥 Followers: {r['followers']}")
        print(f"🔗 Connections: {r['connections']}")
        print(f"📅 Last Activity: {r['last_activity']}")
        print(f"🧭 Activity Type: {r['activity_type']}")
        print(f"🏢 LinkedIn Page: {r['linkedinpage']}")

if __name__ == "__main__":
    main()
