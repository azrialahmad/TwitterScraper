# Twitter Scraper

This project is a simple Twitter scraper that uses Selenium to log in to X.com (formerly Twitter), scrape tweets based on a specified topic or keyword, and save the results to a CSV file using Pandas.

## Features

- **Login to X.com**: Automates the login process to access the search functionality.
- **Scrape Tweets**: Collects tweets based on a user-defined keyword.
- **Save to CSV**: Exports the scraped tweets to a CSV file for easy access and analysis.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Chrome WebDriver (compatible with your Chrome version)
- Required Python packages:
  - `selenium`
  - `pandas`

You can install the required packages using pip:

```bash
pip install selenium pandas
