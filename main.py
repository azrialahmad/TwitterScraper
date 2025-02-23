import time
import random
import os
import pandas as pd
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Function to log in to X.com
def handle_suspicious_activity(phone_email_field):
    # Prompt user for phone number or email
    phone_or_email = input("Enter your phone number (use country code ex: +1) or email address: ")
    phone_email_field.send_keys(phone_or_email)
    phone_email_field.send_keys(Keys.RETURN)
    time.sleep(3)  # Wait for the next page to load

def login_to_x(driver, username, password):
    driver.get("https://x.com/login")
    time.sleep(3)  # Wait for the login page to load

    # Find the username field and enter the username
    try:
        # Wait for the username field to be present
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_field.send_keys(username)
        username_field.send_keys(Keys.RETURN)
        time.sleep(3)  # Wait for the next page to load

        # Check for the phone/email prompt
        try:
            phone_email_field = driver.find_element(By.XPATH, '//input[@name="text"]')
            if phone_email_field.is_displayed():
                handle_suspicious_activity(phone_email_field)
                
        except NoSuchElementException:
            print("No phone/email prompt detected, proceeding to password entry.")

        # Now enter the password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

    except TimeoutException:
        print("Login elements not found. Please check the page structure.")

# Function to set up the WebDriver with proxy support and suppress logs
def setup_driver(proxy=None, username=None, password=None):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)

    # Suppress WebDriver logs
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # If a proxy is provided, set it up
    if proxy:
        if username and password:
            # For authenticated proxies
            chrome_options.add_argument(f'--proxy-server=http://{username}:{password}@{proxy}')
        else:
            # For non-authenticated proxies
            chrome_options.add_argument(f'--proxy-server={proxy}')

    # Set up the WebDriver
    os.environ['PATH'] = r'E:/Chromedriver/chrome-win64'  # Update with the path to your ChromeDriver
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def switch_to_latest(driver):
    try:
        latest_tab = driver.find_element(By.XPATH, '//a[contains(@href, "latest")]')
        latest_tab.click()
        time.sleep(3)  # Wait for the Latest tab to load
    except NoSuchElementException:
        print("Latest tab not found.")

# Function to scrape tweets based on a topic/keyword with pagination
def scrape_topic_tweets(driver, keyword, max_tweets=100):
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://x.com/search?q={encoded_keyword}&src=typed_query"  # Start with Top tweets
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    tweets = []
    attempts = 0
    max_attempts = 5  # Maximum attempts to find new tweets

    while len(tweets) < max_tweets:
        tweet_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        new_tweets_found = False

        for tweet_element in tweet_elements:
            try:
                tweet_text = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                username = tweet_element.find_element(By.XPATH, './/div[@data-testid="User-Name"]').text
                timestamp = tweet_element.find_element(By.XPATH, './/time').get_attribute('datetime')
                
                tweet_data = {
                    'Username': username,
                    'Text': tweet_text,
                    'Timestamp': timestamp
                }
                
                if tweet_data not in tweets:
                    tweets.append(tweet_data)
                    new_tweets_found = True
                    print(f"Scraped tweet: {tweet_text} (Total scraped: {len(tweets)})")
                    if len(tweets) >= max_tweets:
                        break
            except NoSuchElementException:
                continue

        if not new_tweets_found:
            attempts += 1
            print(f"No new tweets found. Attempt {attempts}/{max_attempts}.")
            if attempts >= max_attempts:
                print("Switching to Latest tweets...")
                url = f"https://x.com/search?q={encoded_keyword}&src=typed_query&f=live"  # Switch to Latest tweets
                driver.get(url)
                time.sleep(5)  # Wait for the page to load
                attempts = 0  # Reset attempts for the Latest tweets

        # Scroll down to load more tweets
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(random.uniform(2, 5))  # Random sleep to mimic human behavior

    return tweets

# Function to save tweets to a CSV file
def save_tweets_to_csv(tweets, filename):
    df = pd.DataFrame(tweets)
    df.to_csv(filename, index=False)
    print(f"Saved {len(tweets)} tweets to {filename}")

# Main function to handle user input
def main():
    # User credentials
    username = input("Enter your X.com username: ")
    password = input("Enter your X.com password: ")

    # Proxy configuration (optional)
    use_proxy = input("Do you want to use a proxy? (y/n): ").lower()
    proxy = None
    proxy_username = None
    proxy_password = None

    if use_proxy == 'y':
        proxy = input("Enter proxy IP: ")
        proxy_auth = input("Does the proxy require authentication? (y/n): ").lower()
        if proxy_auth == 'y':
            proxy_username = input("Enter proxy username: ")
            proxy_password = input("Enter proxy password: ")

    # Set up the WebDriver with proxy support
    driver = setup_driver(proxy, proxy_username, proxy_password)

    try:
        # Log in to X.com
        login_to_x(driver, username, password)

        # Scrape tweets
        keyword = input("Enter the topic/keyword: ")
        max_tweets = int(input("Enter the maximum number of tweets to scrape: "))
        tweets = scrape_topic_tweets(driver, keyword, max_tweets)

        # Save tweets to CSV
        filename = input("Enter the filename to save the tweets (e.g., tweets.csv): ")
        save_tweets_to_csv(tweets, filename)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
