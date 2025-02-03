import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# Function to log in to X.com
def login_to_x(driver, username, password):
    driver.get("https://x.com/login")
    time.sleep(3)  # Wait for the login page to load

    # Find the username and password fields and enter your credentials
    username_field = driver.find_element(By.NAME, "text")
    username_field.send_keys(username)
    username_field.send_keys(Keys.RETURN)
    time.sleep(2)  # Wait for the password field to load

    password_field = driver.find_element(By.NAME, "password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)
    time.sleep(5)  # Wait for the login process to complete

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
        time.sleep(5)  # Wait for new tweets to load

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

    # Set up Chrome options
    chrome_options = Options()
    # Remove the headless option to see the browser in action
    # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the WebDriver
    os.environ['PATH'] = r'E:/Chromedriver/chrome-win64' # Update with the path to your ChromeDriver
    driver = webdriver.Chrome(options=chrome_options)

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
