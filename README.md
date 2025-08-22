# Books Data Scraper

A web scraping project that extracts book information from books.toscrape.com using Selenium WebDriver.

## Description

This project scrapes book data including:

- Title
- Category
- Price
- Description
- Rating

The data is collected from all available pages and saved to a CSV file.

## Requirements

- Python 3.x
- Chrome browser
- Required Python packages:

```
selenium
pandas
```

## Setup

1. Install required packages:

```sh
pip install -r requirements.txt
```

2. Download ChromeDriver:

- The project includes ChromeDriver in `chromedriver_win64/` directory
- Make sure the ChromeDriver version matches your Chrome browser version

## Usage

You can run the scraper in two ways:

1. Using the Python script:

```sh
python src/scrapy.py
```

2. Using the Jupyter notebook:

```sh
jupyter notebook test_clawer.ipynb
```

The scraped data will be saved to `data/books_data.csv`.

## Project Structure

```
├── chromedriver_win64/    # ChromeDriver executable and licenses
├── data/                  # Output directory for scraped data
├── src/                   # Source code
│   └── scrapy.py         # Main scraping script
├── test_clawer.ipynb     # Jupyter notebook version
├── requirements.txt       # Python dependencies
└── README.md
```

## Features

- Automatically navigates through all pages
- Handles missing data gracefully
- Opens book details in new tabs
- Includes error handling for timeouts and missing elements
- Maximized browser window for better scraping
