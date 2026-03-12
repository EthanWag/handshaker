from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def start_up(driver, username, password, query) -> int:
    # Go to search URL (will redirect for auth)
    job_query = query.replace(" ", "%20")
    num_results=50
    driver.get(f"https://byu.joinhandshake.com/postings?page=1&per_page={num_results}&job.salary_types%5B%5D=1&sort_direction=desc&sort_column=default&query={job_query}&employment_type_names%5B%5D=Full-Time")

    # Handle login
    byu_login_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "sso-button"))
    )
    byu_login_btn.click()

    # Wait for the username and password fields to be visible
    username_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    username_input.send_keys(username)

    password_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    password_input.send_keys(password)

    password_input.send_keys(Keys.ENTER)  # Submit login

    # Wait for DUO authentication and other redirects
    
    print("Sending Duo Request!!")
    sleep(20)

    auth_button = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.ID, "trust-browser-button"))
    )
    auth_button.click()
    sleep(10)

    # Check if we are on the explore page
    current_url = driver.current_url
    if "explore" in current_url:  # If we're on the explore page
        print("Redirecting to job postings page...")
        # Manually navigate to the job postings page
        driver.get(f"https://byu.joinhandshake.com/postings?page=1&per_page={num_results}&sort_direction=desc&sort_column=default&query={job_query}&job.salary_types%5B%5D=1&employment_type_names%5B%5D=Full-Time&job.job_types%5B%5D=9")
        sleep(5)  # Wait for the page to load

    return True


def apply_to_jobs(driver, non_quick_apply_urls,resume,transcript,cover_letter, count=None):


    if count is None:
        count = float('inf')  # Set to infinity if no count is provided

    jobs_applied = 0

    # Wait for postings section to be visible on the job search page
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@data-hook, 'job-result-card')]"))
        )
        print("Job postings found!")
    
    except Exception as e:
        print("Error: Job postings not found.")
        print(f"Exception: {str(e)}")
        driver.quit()
        return
    

    # Find all job postings on the current page
    postings = driver.find_elements(By.XPATH, "//div[contains(@data-hook, 'job-result-card')]")
    print(f"Finding postings on the current page...")

    job_urls = []
    for posting in postings:

        try: 
            posting.get_attribute("innerHTML")  # This is to force the lazy loading of the job link, otherwise it won't be found when we try to find it below
            job_link = posting.find_element(By.XPATH, ".//a[@role='button']")
            job_url = job_link.get_attribute("href")
            job_urls.append(job_url)
        except Exception as e:
            print("Error finding job link for a posting, skipping.")
            print(f"Exception: {str(e)}")
            continue

    for url in job_urls:


        if jobs_applied >= count:
            print(f"Reached the limit of {count} applications for this session.")
            break

        driver.get(url)

        # Check for the 'Apply' button using its aria-label
        try:
            apply_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Apply"]'))
            )
            apply_btn.click()
            sleep(2)
        except Exception as e:
            print("Apply button not found or not clickable, skipping.")
            # Save the job URL for manual review
            job_url = driver.current_url
            non_quick_apply_urls.append(job_url)
            print(f"Saved for review: {job_url}")
            continue

        try:

            # need to upload transcripts and cover letters
            # for now just skips

            find_and_click_submit_btn(driver)
            print("Applied to job!")
            jobs_applied += 1

        except Exception as e:
            continue


        

def find_and_click_submit_btn(driver, timeout=10):
    """Find and click the Submit Application button with waits."""
    try:
        wait = WebDriverWait(driver, timeout)
        submit_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(., "Submit Application")]'))
        )
        submit_btn.click()
        return True
    except TimeoutException:
        print("Submit button not found or not clickable")
        return False
    
def is_modal_visible(driver):
    """Check if the apply modal is still visible."""
    try:
        apply_modal = driver.find_elements(By.XPATH, '//span[@data-hook="apply-modal-content"]')
        return len(apply_modal) > 0
    except:
        return False
    
def dismiss_modal(driver, timeout=10):
    """Attempt to dismiss the modal."""
    try:
        dismiss_btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "style__dismiss___Zotdc"))
        )
        dismiss_btn.click()
        print("Dismissed the modal.")
        return True
    except TimeoutException:
        print("Dismiss button not found.")
        return False