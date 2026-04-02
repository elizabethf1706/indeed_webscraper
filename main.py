from job_scraper_utils import *

"""
List of countries url.
"""
nigeria = 'https://ng.indeed.com'
united_kingdom = 'https://uk.indeed.com'
united_states = 'https://www.indeed.com'
canada = 'https://ca.indeed.com'
germany = 'https://de.indeed.com'
australia = 'https://au.indeed.com'
south_africa = 'https://za.indeed.com'
sweden = 'https://se.indeed.com'
singapore = 'https://www.indeed.com.sg'
switzerland = 'https://www.indeed.ch'
united_arab_emirates = 'https://www.indeed.ae'
new_zealand = 'https://nz.indeed.com'
india = 'https://www.indeed.co.in'
france = 'https://www.indeed.fr'
italy = 'https://it.indeed.com'
spain = 'https://www.indeed.es'
japan = 'https://jp.indeed.com'
south_korea = 'https://kr.indeed.com'
brazil = 'https://www.indeed.com.br'
mexico = 'https://www.indeed.com.mx'
china = 'https://cn.indeed.com'
saudi_arabia = 'https://sa.indeed.com'
egypt = 'https://eg.indeed.com'
thailand = 'https://th.indeed.com'
vietnam = 'https://vn.indeed.com'
argentina = 'https://ar.indeed.com'
ireland = 'https://ie.indeed.com'


def main():
    driver = configure_webdriver()
    country = united_states
    job_position = 'software developer'
    job_location = 'remote'
    date_posted = 20

    csv_file = get_csv_path(job_position, job_location)
    print(f"Saving results live to: {csv_file}")

    try:
        search_jobs(driver, country, job_position, job_location, date_posted)
        count = scrape_job_data(driver, country, csv_file)

        if count == 0:
            print("No results found.")
        else:
            print(f"Done. {count} jobs saved to: {csv_file}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
