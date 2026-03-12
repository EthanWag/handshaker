import os
import json
import asyncio
from dotenv import load_dotenv  # Import the dotenv package
from time import sleep  # Import sleep function
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Ensure this import is here
from selenium.webdriver.support.ui import WebDriverWait  # Import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # Import EC
from selenium.webdriver.common.by import By  # Import By for locating elements
from handshake.bot import start_up, apply_to_jobs 
import json  # <-- Make sure this line is included


async def applier(job_title:str = "software engineer", count: int = None):

    # Initialize a list to store non-Quick Apply URLs for later review
    non_quick_apply_urls = []

    # Load environment variables from the .env file
    load_dotenv()

    # Get username and password from environment variables
    username = os.getenv("BYU_USERNAME")
    password = os.getenv("BYU_PASSWORD")
    resume = os.getenv("RESUME_NAME")

    # Check if username and password are set
    if not username or not password or not resume:
        return "Error: Username and password and resume must be provided in the .env file."

    # Run the synchronous scraper in a thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _run_scraper, username, password, resume, job_title, count, non_quick_apply_urls)
    
    return result


def _run_scraper(username, password, resume, job_title, count, non_quick_apply_urls):

    # Initialize web driver
    # I don't like having to see what is going on in the browser, maybe that is a mistake
    chrome_options = Options()

    chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--window-size=1920,1080") # for debugging purposes
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Perform the startup process (login and initial page load)
        if start_up(driver, username, password, job_title.lower()):
            # Apply to jobs on the first page and handle pagination
            while True:
                # Apply to jobs on the current page
                apply_to_jobs(driver, non_quick_apply_urls, resume, None, None, count)

                # Check for next page once all postings on the current page are processed
                def go_to_next_page():
                    try:
                        next_page_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[@data-hook="search-pagination-next"]'))
                        )
                        next_page_btn.click()
                        print("Moving to the next page...")
                        sleep(10)  # Give time for the next page to load
                        return True  # Return True if next page is successfully loaded
                    except Exception as e:
                        print("No next page! Exiting...")
                        return False  # Return False if there is no next page

                # Call function to go to the next page
                if go_to_next_page():
                    # Once next page is loaded, apply to jobs on this page as well
                    apply_to_jobs(driver, non_quick_apply_urls, resume, None, None, count)
                else:
                    # break the loop if there is no next page
                    break
    finally:
        # Close the driver after processing all pages
        driver.quit()

    # Save non-Quick Apply URLs to a JSON file after processing all pages
    '''
    with open("non_quick_apply_urls.json", "w") as json_file:
        json.dump(non_quick_apply_urls, json_file, indent=4)
    '''
    result = f"Applied to jobs! Saved {len(non_quick_apply_urls)} non-Quick Apply URLs to 'non_quick_apply_urls.json'."
    print(result)
    return result


if __name__ == "__main__":
    asyncio.run(applier())

