import os
from typing import KeysView
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

class WebScraper:
    def __init__(self):
        # Initialize the Chrome web driver
        self.install = ChromeDriverManager().install()
        self.cService = webdriver.ChromeService(executable_path=self.install)
        self.driver = webdriver.Chrome(service=self.cService)
        self.download_dir = os.path.join(os.getcwd(), 'scraped_photos')
        self.picture_number_incrementer = 0
        self.page_incrementer = 0

    def scrape_urls(self, url):
        # Navigate to the website
        self.driver.get(url)
        urls = []

        try:
            while True:
                # Locate the <ul> element
                ul_element = self.driver.find_element(By.CLASS_NAME, 'css-8tedj6')

                # Find all <li> elements within the <ul> element
                li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

                # Iterate through the <li> elements and extract the URLs
                for li_element in li_elements:
                    # Locate the <a> element within the <div>
                    try:
                        a_element = li_element.find_element(By.TAG_NAME, 'a')
                        li_url = a_element.get_attribute('href')
                        # Append the URL to the list
                        urls.append(li_url)
                    except:
                        continue

                # Locate and click the "Next" button to go to the next page
                next_button = self.driver.find_element(By.XPATH, '//a[@data-testid="paginator-navigation-button" and contains(@class, "css-xixru3") and contains(span, "next page")]')
                if next_button:
                    self.page_incrementer += 1
                    if self.page_incrementer > 10:
                        break
                    next_button.click()
                    # Wait for a moment to allow the new page to load
                    time.sleep(2)
                else:
                    break  # No "Next" button found, exit the loop

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        return urls

    def extract_photos(self, urls):
        # Extract photos from a list of URLs
        for url in urls:
            self.driver.get(url)
            try:
                photo_button = self.driver.find_element(By.XPATH, '//div[@data-testid="listing-details__gallery-preview single-image-full"]//button')
                if photo_button:
                    photo_button.click()
                                        # Wait for a moment to allow the photo slideshow to load
                    time.sleep(2)
                    # last_height = self.driver.execute_script("return document.body.scrollHeight")
                    # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # element = self.driver.find_element(By.CLASS_NAME, "css-1fjvlsb").sendKeys(KeysView.PAGE_DOWN)
                    # self.driver.execute_script("arguments[0].scrollIntoView();", element)

                    try:
                        # Locate the <div> element containing the photos
                        img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                        # photos_figures = self.driver.find_elements(By.TAG_NAME, 'figure')

                        # Find all <img> elements within the <div>
                        #img_elements = photos_div.find_elements(By.TAG_NAME, 'img')

                        # Iterate through the <img> elements and save each photo to the folder
                        img_elements = img_elements[3:-14]
                        for i, img in enumerate(img_elements):
                            try:
                                src = img.get_attribute('src')
                                if src:
                                    # Get the image content
                                    response = requests.get(src)

                                    if response.status_code == 200:
                                        # Construct the file path
                                        file_name = f'photo_{self.picture_number_incrementer}.jpg'
                                        file_path = os.path.join(self.download_dir, file_name)

                                        self.picture_number_incrementer += 1

                                        # Save the image to the folder
                                        with open(file_path, 'wb') as f:
                                            f.write(response.content)

                                        print(f"Saved photo {self.picture_number_incrementer} to {file_path}")
                                    else:
                                        print(f"Failed to download photo {self.picture_number_incrementer}")
                            except Exception as e:
                                print(f"An error occurred while saving photos - cant get src attribute: {str(e)}")
                                continue

                    except Exception as e:
                        print(f"An error occurred while saving photos: {str(e)}")

                else:
                    print(f"No photo slideshow button found on {url}")
                    continue
            except Exception as e:
                print(f"An error occurred while trying to open the photo slideshow: {str(e)}")
                continue
            # You can add code here to extract and process photos from the current URL
            # For example, you can locate the photo elements and download them

    def close_driver(self):
        # Close the web driver
        self.driver.quit()

# Example usage:
if __name__ == "__main__":
    # Initialize the web scraper
    scraper = WebScraper()

    # URL of the website to scrape
    target_url = "https://www.domain.com.au/sale/phillip-island-vic-3925/?ptype=duplex,free-standing,new-home-designs,new-house-land,semi-detached,terrace,town-house,villa&excludeunderoffer=1"

    # Collect URLs from the website
    #scraped_urls = ['https://www.domain.com.au/19-21-niagara-lane-melbourne-vic-3000-2018725443']
    scraped_urls = scraper.scrape_urls(target_url)

    # Extract photos from the collected URLs
    scraper.extract_photos(scraped_urls)

    # Close the web driver
    scraper.close_driver()