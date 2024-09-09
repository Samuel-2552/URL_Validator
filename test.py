from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set up the driver
service = Service("D:/chromedriver-win64/chromedriver.exe")  # Path to your ChromeDriver executable

def get_final_url(driver, url):
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to execute and handle redirections
    return driver.current_url

def process_urls(input_file, output_file):
    # Read URLs from input file
    with open(input_file, 'r') as file:
        urls = file.readlines()
    
    # Set up WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        with open(output_file, 'w') as file:
            for url in urls:
                url = url.strip()
                if url:  # Check if the URL is not an empty string
                    final_url = get_final_url(driver, url)
                    file.write(f"{final_url}\n")
                    print(f"Processed: {url} -> {final_url}")
    finally:
        driver.quit()  # Clean up and close the browser

# Define file paths
input_file = 'input_urls.txt'  # File with list of URLs
output_file = 'output_urls.txt'  # File to write final URLs

# Process URLs
process_urls(input_file, output_file)
