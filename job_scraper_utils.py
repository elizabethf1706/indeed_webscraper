import os
import time

import pandas as pd
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


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


def search_jobs(driver, country, job_position, job_location, date_posted):
    full_url = f'{country}/jobs?q={"+".join(job_position.split())}&l={job_location}&fromage={date_posted}'
    print(full_url)
    driver.get(full_url)
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

    return full_url


def scrape_job_data(driver, country, csv_path):
    job_count = 0

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        f.write('Job Title,Job Description\n')

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

            # Visit job page to get description
            job_description = None
            if link_full:
                try:
                    driver.get(link_full)
                    time.sleep(1)
                    detail_soup = BeautifulSoup(driver.page_source, 'lxml')
                    desc_div = detail_soup.find('div', {'id': 'jobDescriptionText'})
                    if desc_div:
                        job_description = desc_div.get_text(separator='\n').strip()
                    driver.back()
                    time.sleep(1)
                except Exception:
                    pass

            # Write row immediately to file
            row = pd.DataFrame([{'Job Title': job_title, 'Job Description': job_description}])
            row.to_csv(csv_path, mode='a', header=False, index=False)
            job_count += 1
            print(f"Saved job {job_count}: {job_title}")

        try:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')
            driver.get(country + next_page)
            time.sleep(2)
        except:
            break

    return job_count


def get_csv_path(job_position, job_location):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    return os.path.join(desktop_path, f'{job_position}_{job_location}.csv')
