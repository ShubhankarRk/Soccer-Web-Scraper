# Soccer-Web-Scraper
This project automates the extraction, cleaning, and storage of soccer match data(WhoScored) from the web. By utilizing Python-based web scraping tools and cloud database integration, it enables efficient data collection and organization for further analysis.

# Features
Web Scraping: Extracts soccer match event data from WhoScored.com using Selenium and BeautifulSoup.
Data Cleaning & Transformation: Processes raw data into a structured format with pandas and numpy.
Cloud Database Integration: Stores cleaned data in a Supabase PostgreSQL database for easy querying and analysis.
Player & Event Data Modeling: Uses pydantic for structured data modeling of match events and player information.
Automation: Fully automated pipeline to scrape, clean, and ingest soccer match data.


# Technologies Used
Web Scraping: BeautifulSoup, Selenium
Data Processing: pandas, numpy
Data Modeling: pydantic
Cloud Database: Supabase (supabase-py)
Programming Language: Python

# Pipeline Steps
Source soccer match data from WhoScored.com.
Build a Python-based scraping pipeline using Selenium and BeautifulSoup.
Clean and transform raw data into a structured format with pandas.
Use pydantic models to validate and structure match events and player data.
Store processed data in a Supabase PostgreSQL database.
Query the database for insights or further analysis.
