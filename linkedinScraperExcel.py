# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# import pandas as pd
# import time
# import random
# import re
# import os

# # 🔐 LinkedIn credentials
# USERNAME = "anesh@fiveoak.com"
# PASSWORD = "Zlatan@123"

# # === Setup Chrome Driver ===
# def setup_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     return webdriver.Chrome(options=options)

# # === Login to LinkedIn ===
# def login_linkedin(driver, username, password):
#     driver.get("https://www.linkedin.com/login")
#     try:
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
#         WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
#         time.sleep(5)
#     except Exception as e:
#         print(f"❌ Login failed: {e}")
#         driver.quit()
#         exit()

# # === Load LinkedIn Profile URLs from Excel ===
# def load_profile_urls_from_excel(file_path):
#     try:
#         if not os.path.exists(file_path):
#             print(f"❌ File not found at: {file_path}")
#             return []

#         df = pd.read_excel(file_path)
#         urls = []
#         for col in df.columns:
#             col_urls = df[col].dropna().astype(str)
#             profile_urls = col_urls[col_urls.str.contains("linkedin.com/in", case=False)].tolist()
#             urls.extend(profile_urls)

#         print(f"✅ Loaded {len(urls)} LinkedIn URLs from Excel.")
#         return urls
#     except Exception as e:
#         print(f"❌ Failed to load Excel file: {e}")
#         return []

# # === Detect LinkedIn Company Page ===
# def detect_linkedin_company_page(driver, soup):
#     linkedin_page = "NO"
#     original_window = driver.current_window_handle

#     try:
#         # === Primary: Look for current role in experience section ===
#         exp_section = soup.find('section', {'id': re.compile(r'experience.*', re.IGNORECASE)})
#         if exp_section:
#             roles = exp_section.find_all('li')
#             for role in roles:
#                 date_span = role.find('span', string=re.compile(r'Present', re.IGNORECASE))
#                 if date_span:
#                     link = role.find('a', href=True)
#                     if link and "linkedin.com/company/" in link['href']:
#                         href = link['href']
#                         print(f"🔗 Found current company link: {href}")
#                         driver.execute_script("window.open(arguments[0]);", href)
#                         WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))

#                         for handle in driver.window_handles:
#                             if handle != original_window:
#                                 driver.switch_to.window(handle)
#                                 break

#                         time.sleep(3)
#                         current_url = driver.current_url
#                         page_title = driver.title
#                         company_soup = BeautifulSoup(driver.page_source, 'html.parser')

#                         # === Content validation ===
#                         company_logo = company_soup.find('img', {'alt': re.compile(r'logo', re.IGNORECASE)})
#                         has_followers = company_soup.find(string=re.compile(r'followers', re.IGNORECASE))
#                         has_overview = company_soup.find(string=re.compile(r'about', re.IGNORECASE))

#                         if "search" in current_url or "search results" in page_title.lower():
#                             print(f"🚫 Redirected to search: {current_url}")
#                         elif company_logo or has_followers or has_overview:
#                             linkedin_page = "YES"
#                         else:
#                             print(f"⚠️ Suspicious company page: {current_url} — no content found")

#                         driver.close()
#                         driver.switch_to.window(original_window)
#                         return linkedin_page

#         # === Fallback: Scan all links for any valid company page ===
#         all_links = soup.find_all('a', href=True)
#         fallback_section = soup.find('section', {'id': re.compile(r'experience.*', re.IGNORECASE)})
   
#         print(f"🔍 Found {len(all_links)} total links on page")

#         for link in all_links:
#             href = link['href']
#             if "linkedin.com/company/" in href and \
#                not any(x in href for x in ["admin", "inbox", "search/results/all"]):
#                 print(f"🔍 Found fallback company link: {href}")
#                 driver.execute_script("window.open(arguments[0]);", href)
#                 WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))

#                 for handle in driver.window_handles:
#                     if handle != original_window:
#                         driver.switch_to.window(handle)
#                         break

#                 time.sleep(3)
#                 current_url = driver.current_url
#                 page_title = driver.title
#                 company_soup = BeautifulSoup(driver.page_source, 'html.parser')

#                 company_logo = company_soup.find('img', {'alt': re.compile(r'logo', re.IGNORECASE)})
#                 has_followers = company_soup.find(string=re.compile(r'followers', re.IGNORECASE))
#                 has_overview = company_soup.find(string=re.compile(r'about', re.IGNORECASE))

#                 if "search" in current_url or "search results" in page_title.lower():
#                     print(f"🚫 Redirected to search: {current_url}")
#                 elif company_logo or has_followers or has_overview:
#                     linkedin_page = "YES"
#                 else:
#                     print(f"⚠️ Suspicious fallback page: {current_url} — no content found")

#                 driver.close()
#                 driver.switch_to.window(original_window)
#                 return linkedin_page

#     except Exception as e:
#         print(f"❌ Error detecting company page: {e}")
#         linkedin_page = "NO"

#     return linkedin_page


# # === Scrape LinkedIn Profile ===
# def scrape_profile(driver, url):
#     driver.get(url)
#     time.sleep(random.uniform(5, 8))
#     soup = BeautifulSoup(driver.page_source, 'html.parser')

#     # Connections
#     connection_text = "Not found"
#     all_spans = soup.find_all('span')
#     for span in all_spans:
#         if span.text and 'connections' in span.text.lower():
#             connection_text = span.text.strip()
#             break

#     # Followers
#     follower_text = "Not found"
#     for span in all_spans:
#         if span.text and 'followers' in span.text.lower():
#             follower_text = span.text.strip()
#             break

#     # Last Activity
#     last_activity = "No public posts found"
#     activity_type = "None"
#     time_pattern = re.compile(r'\b(\d+\s?(w|d|mo|h|week|day|month|hour)s?)\b', re.IGNORECASE)
#     posts = soup.find_all('div', class_='feed-shared-update-v2')
#     for post in posts:
#         for span in post.find_all('span'):
#             text = span.get_text(strip=True)
#             if time_pattern.search(text):
#                 last_activity = time_pattern.search(text).group(1)
#                 activity_type = "posted"
#                 break
#         if last_activity != "No public posts found":
#             break

#     if last_activity == "No public posts found":
#         for span in all_spans:
#             text = span.get_text(strip=True).lower()
#             if 'commented on a post' in text and time_pattern.search(text):
#                 last_activity = time_pattern.search(text).group(1)
#                 activity_type = "commented"
#                 break
#             elif 'reposted' in text and time_pattern.search(text):
#                 last_activity = time_pattern.search(text).group(1)
#                 activity_type = "reposted"
#                 break
#             elif 'liked this post' in text and time_pattern.search(text):
#                 last_activity = time_pattern.search(text).group(1)
#                 activity_type = "liked"
#                 break

#     linkedin_page = detect_linkedin_company_page(driver, soup)

#     return {
#         "Linkedin URL": url,
#         "Connections Count": connection_text,
#         "Followers": follower_text,
#         "Last Activity": last_activity,
#         "Activity Type": activity_type,
#         "Company Page": "Yes" if linkedin_page == "YES" else "No"
#     }

# # === Main Execution ===
# def main():
#     input_path = "linkedinUrls.xlsx"
#     output_path = "linkedin_enriched.xlsx"

#     PROFILE_URLS = load_profile_urls_from_excel(input_path)
#     if not PROFILE_URLS:
#         print("⚠️ No profile URLs found. Exiting.")
#         return

#     driver = setup_driver()
#     login_linkedin(driver, USERNAME, PASSWORD)
#     results = []

#     for url in PROFILE_URLS:
#         try:
#             data = scrape_profile(driver, url)
#             results.append(data)
#             print(f"✅ Scraped: {url}")
#         except Exception as e:
#             print(f"❌ Error scraping {url}: {e}")

#     driver.quit()

#     # Export to Excel
#     if results:
#         df_out = pd.DataFrame(results)
#         try:
#             df_out.to_excel(output_path, index=False)
#             print(f"\n📁 Saved {len(results)} profiles to {output_path}")
#         except PermissionError:
#             fallback_path = output_path.replace(".xlsx", "_backup.xlsx")
#             df_out.to_excel(fallback_path, index=False)
#             print(f"\n⚠️ Original file was open or locked. Saved to fallback: {fallback_path}")

# if __name__ == "__main__":
#     main()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re
import os

# 🔐 LinkedIn credentials
USERNAME = "anesh@fiveoak.com"
PASSWORD = "Zlatan@123"

# === Setup Chrome Driver ===
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return webdriver.Chrome(options=options)

# === Login to LinkedIn ===
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

# === Load LinkedIn Profile URLs from Excel ===
def load_profile_urls_from_excel(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found at: {file_path}")
            return []

        df = pd.read_excel(file_path)
        urls = []
        for col in df.columns:
            col_urls = df[col].dropna().astype(str)
            profile_urls = col_urls[col_urls.str.contains("linkedin.com/in", case=False)].tolist()
            urls.extend(profile_urls)

        print(f"✅ Loaded {len(urls)} LinkedIn URLs from Excel.")
        return urls
    except Exception as e:
        print(f"❌ Failed to load Excel file: {e}")
        return []

# === Helper: Validate Company Link ===
def is_valid_company_link(href):
    href = href.lower()
    if "linkedin.com/school/" in href:
        print(f"🏫 Rejected school link: {href}")
        return False
    if any(school_keyword in href for school_keyword in ["university", "college", "school", "edu", "academy", "institute"]):
        print(f"🏫 Rejected educational link: {href}")
        return False
    if "linkedin.com/groups/" in href:
        print(f"👥 Rejected group link: {href}")
        return False
    if "linkedin.com/showcase/" in href:
        print(f"📢 Rejected showcase link: {href}")
        return False
    if "linkedin.com/company/" in href:
        if any(x in href for x in ["admin", "inbox", "search/results/all"]):
            print(f"🚫 Rejected company link (internal): {href}")
            return False
        return True
    return False


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
                    if link and is_valid_company_link(link['href']):
                        href = link['href']
                        print(f"🔗 Found current company link: {href}")
                        driver.execute_script("window.open(arguments[0]);", href)
                        WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))

                        for handle in driver.window_handles:
                            if handle != original_window:
                                driver.switch_to.window(handle)
                                break

                        time.sleep(3)
                        current_url = driver.current_url
                        page_title = driver.title
                        company_soup = BeautifulSoup(driver.page_source, 'html.parser')
                         # 🔒 Final content-level school rejection
                        page_text = company_soup.get_text().lower()
                        if any(term in page_text for term in ["university", "college", "school", "academy", "institute", "education"]):
                            print(f"🏫 Rejected page based on content: {current_url}")
                            driver.close()
                            driver.switch_to.window(original_window)
                            continue


                        company_logo = company_soup.find('img', {'alt': re.compile(r'logo', re.IGNORECASE)})
                        has_followers = company_soup.find(string=re.compile(r'followers', re.IGNORECASE))
                        has_overview = company_soup.find(string=re.compile(r'about', re.IGNORECASE))

                        if "search" in current_url or "search results" in page_title.lower() or page_title.strip().lower() == "linkedin":
                            print(f"🚫 Redirected to search or generic page: {current_url}")
                        elif (company_logo and has_followers) or (has_followers and has_overview) or (company_logo and has_overview):
                            linkedin_page = "YES"
                        else:
                            print(f"⚠️ Weak or suspicious company page: {current_url} — missing key elements")

                        driver.close()
                        driver.switch_to.window(original_window)
                        return linkedin_page

        # === Fallback: Scan all links only if experience section fails ===
        all_links = soup.find_all('a', href=True)
        print(f"🔍 Found {len(all_links)} total links on page")

        for link in all_links:
            href = link['href']
            if not is_valid_company_link(href):
                continue

            print(f"🔍 Found fallback company link: {href}")
            driver.execute_script("window.open(arguments[0]);", href)
            WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))

            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    break

            time.sleep(3)
            current_url = driver.current_url
            page_title = driver.title
            company_soup = BeautifulSoup(driver.page_source, 'html.parser')

            company_logo = company_soup.find('img', {'alt': re.compile(r'logo', re.IGNORECASE)})
            has_followers = company_soup.find(string=re.compile(r'followers', re.IGNORECASE))
            has_overview = company_soup.find(string=re.compile(r'about', re.IGNORECASE))

            if "search" in current_url or "search results" in page_title.lower() or page_title.strip().lower() == "linkedin":
                print(f"🚫 Redirected to search or generic page: {current_url}")
            elif (company_logo and has_followers) or (has_followers and has_overview) or (company_logo and has_overview):
                linkedin_page = "YES"
            else:
                print(f"⚠️ Weak or suspicious fallback page: {current_url} — missing key elements")

            driver.close()
            driver.switch_to.window(original_window)
            return linkedin_page

    except Exception as e:
        print(f"❌ Error detecting company page: {e}")
        linkedin_page = "NO"

    return linkedin_page


# === Scrape LinkedIn Profile ===
def scrape_profile(driver, url):
    driver.get(url)
    time.sleep(random.uniform(5, 8))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Connections
    connection_text = "Not found"
    all_spans = soup.find_all('span')
    for span in all_spans:
        if span.text and 'connections' in span.text.lower():
            connection_text = span.text.strip()
            break

    # Followers
    follower_text = "Not found"
    for span in all_spans:
        if span.text and 'followers' in span.text.lower():
            follower_text = span.text.strip()
            break

    # Last Activity
    last_activity = "No public posts found"
    activity_type = "None"
    time_pattern = re.compile(r'\b(\d+\s?(w|d|mo|h|week|day|month|hour)s?)\b', re.IGNORECASE)
    posts = soup.find_all('div', class_='feed-shared-update-v2')
    for post in posts:
        for span in post.find_all('span'):
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

    linkedin_page = detect_linkedin_company_page(driver, soup)

    return {
        "Linkedin URL": url,
        "Connections Count": connection_text,
        "Followers": follower_text,
        "Last Activity": last_activity,
        "Activity Type": activity_type,
        "Company Page": "Yes" if linkedin_page == "YES" else "No"
    }

# === Main Execution ===
def main():
    input_path = "linkedinUrls.xlsx"
    output_path = "linkedin_enriched.xlsx"

    PROFILE_URLS = load_profile_urls_from_excel(input_path)
    if not PROFILE_URLS:
        print("⚠️ No profile URLs found. Exiting.")
        return

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

    # Export to Excel
    if results:
        df_out = pd.DataFrame(results)
        try:
            df_out.to_excel(output_path, index=False)
            print(f"\n📁 Saved {len(results)} profiles to {output_path}")
        except PermissionError:
            fallback_path = output_path.replace(".xlsx", "_backup.xlsx")
            df_out.to_excel(fallback_path, index=False)
            print(f"\n⚠️ Original file was open or locked. Saved to fallback: {fallback_path}")

if __name__ == "__main__":
    main()
