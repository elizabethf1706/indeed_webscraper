from urllib.parse import urlparse
from job_scraper_utils import *


def main():
    url = 'https://www.indeed.com/jobs?q=&l=Remote&radius=35&from=searchOnDesktopSerp&vjk=adc154f7daece3cd'

    country = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    driver = configure_webdriver()

    try:
        search_jobs(driver, url)
        scrape_job_data(driver, country)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
