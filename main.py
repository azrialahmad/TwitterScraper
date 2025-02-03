import time
import random
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

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
    username_field = driver.find_element(By.NAME, "text")
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
    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for the login process to complete


# Function to set up the WebDriver with proxy support
def setup_driver(proxy=None, username=None, password=None):
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")

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

# Function to scrape tweets based on a topic/keyword with pagination
def scrape_topic_tweets(driver, keyword, max_tweets=50):
    url = f"https://x.com/search?q={keyword}&src=typed_query"
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    tweets = []
    while len(tweets) < max_tweets:
        tweet_elements = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        for tweet_element in tweet_elements:
            try:
                tweet_text = tweet_element.find_element(By.XPATH, './/div[@data-testid="tweetText"]').text
                if tweet_text not in tweets:
                    tweets.append(tweet_text)
                    if len(tweets) >= max_tweets:
                        break
            except NoSuchElementException:
                continue

        # Scroll down to load more tweets
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(random.uniform(2, 5))  # Random sleep to mimic human behavior

        # Check if we have reached the end of the page
        if len(tweet_elements) == len(driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')):
            break

    return tweets

# Function to save tweets to a CSV file
def save_tweets_to_csv(tweets, filename):
    df = pd.DataFrame(tweets, columns=["Tweet"])
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
        save_tweets_to_csv(tweets, "scraped_tweets.csv")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
