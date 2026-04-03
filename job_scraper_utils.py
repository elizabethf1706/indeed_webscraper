import os
import time

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ai import ai_evaluate_job


global total_jobs


def configure_webdriver():
    profile_dir = os.path.join(os.path.expanduser("~"), "indeed_chrome_profile")
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={profile_dir}")
    driver = uc.Chrome(options=options, version_main=146)
    return driver


def search_jobs(driver, url):
    driver.get(url)
    input("If prompted to log in or complete a Cloudflare check, do so now. Then press Enter to continue...")
    global total_jobs
    try:
        job_count_element = driver.find_element(By.XPATH,
                                                '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]')
        total_jobs = job_count_element.find_element(By.XPATH, './span').text
        print(f"{total_jobs} found")
    except NoSuchElementException:
        print("No job count found")
        total_jobs = "Unknown"


def scrape_job_data(driver, country):
    evaluated = 0
    saved = 0

    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        boxes = soup.find_all('div', class_='job_seen_beacon')

        for i in boxes:
            # Get job title
            try:
                job_title = i.find('a', class_=lambda x: x and 'JobTitle' in x).text.strip()
            except AttributeError:
                try:
                    job_title = i.find('span', id=lambda x: x and 'jobTitle-' in str(x)).text.strip()
                except AttributeError:
                    job_title = None

            # Get link to job detail page
            try:
                link = i.find('a', {'data-jk': True}).get('href')
                link_full = country + link
            except (AttributeError, TypeError):
                try:
                    link_full = country + i.find('a', class_=lambda x: x and 'JobTitle' in x).get('href')
                except (AttributeError, TypeError):
                    link_full = None

            if not link_full:
                continue

            # Visit job detail page
            try:
                driver.get(link_full)
                time.sleep(1)

                detail_soup = BeautifulSoup(driver.page_source, 'lxml')
                desc_div = detail_soup.find('div', {'id': 'jobDescriptionText'})
                job_description = desc_div.get_text(separator='\n').strip() if desc_div else None

                evaluated += 1
                print(f"[{evaluated}] Evaluating: {job_title}")

                if job_description and ai_evaluate_job(job_title, job_description):
                    # Click the Save button on the detail page
                    try:
                        save_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[.//*[local-name()="title" and text()="save-icon"]]'))
                        )
                        save_btn.click()
                        saved += 1
                        print(f"  -> SAVED ({saved} total saved)")
                    except Exception:
                        print(f"  -> AI said yes but could not find Save button")
                else:
                    print(f"  -> skipped")

                driver.back()
                time.sleep(1)

            except Exception as e:
                print(f"  -> error processing job: {e}")
                continue

        try:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')
            driver.get(country + next_page)
            time.sleep(2)
        except:
            break

    print(f"\nDone. Evaluated {evaluated} jobs, saved {saved}.")
    return evaluated, saved
