import os
import random
from typing import KeysView
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.keys import Keys
from PulseAiSqlite import PulseAiSqlite
from scraperFloorPlanClassifier import ScraperFloorplanClassifier

class WebScraper:
    def __init__(self):
        # Initialize the Chrome web driver
        self.install = ChromeDriverManager().install()
        self.cService = webdriver.ChromeService(executable_path=self.install)
        self.driver = webdriver.Chrome(service=self.cService)
        self.download_dir = os.path.join(os.getcwd(), 'scraped_photos\property_photos')
        self.processed_dir = os.path.join(os.getcwd(), 'scraped_photos\processed_photos')
        self.floor_plan_dir_full_path = os.path.join(os.getcwd(), 'scraped_photos\\floorplan')
        self.floor_plan_local_path = 'scraped_photos\\floorplan'
        self.picture_number_incrementer = 0
        self.page_incrementer = 0
        self.page_incrementer_stop = 15
        self.context = PulseAiSqlite('../propertypulseai')
        self.floor_plan_classifer = ScraperFloorplanClassifier()

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
                    if self.page_incrementer > self.page_incrementer_stop:
                        break
                    next_button.click()
                    # Wait for a moment to allow the new page to load
                    random_sleep_time = random.uniform(1, 6)

                    time.sleep(random_sleep_time)
                else:
                    break  # No "Next" button found, exit the loop

        except Exception as e:
            print(f"An error occurred: {str(e)}")

        return urls

    def extract_property_information(self, urls):
        # Extract photos from a list of URLs
        for url in urls:
            self.driver.get(url)
            time.sleep(2)
            address_div_element = self.driver.find_element(By.CSS_SELECTOR, 'div[data-testid="listing-details__button-copy-wrapper"]')
            address_raw_str = address_div_element.find_element(By.TAG_NAME, 'h1').text
            street_address, city, state, postcode = self.parse_address(address_raw_str)
            full_property_address_string = f"{street_address}_{city}_{state}_{postcode}"
            # / character is found in addresses
            # was causing issues when trying to save to file
            # replacing it with -
            full_property_address_string = full_property_address_string.replace('/', '-')

            if street_address == None or city == None or state == None or postcode == None:
                print(f"Failed to parse address from {url}")
                continue

            if self.context.search_inspector_property(street_address, city, state, postcode, 'Australia') != None:
                print(f"Property {street_address} already exists in the database")
                continue

            # Add the property to the database
            property_id = self.context.add_inspector_property(street_address, city, state, postcode, 'Australia')

            # add property url which has id of 1 for property website which references 
            # DOMAIN.COM.AU
            self.context.add_inspector_property_url(property_id, 1, url)
            


            try:
                photo_button = self.driver.find_element(By.XPATH, '//div[@data-testid="listing-details__gallery-preview single-image-full"]//button')
                if photo_button:
                    photo_button.click()
                    # Wait for a moment to allow the photo slideshow to load
                    random_sleep_time = random.uniform(1, 6)

                    time.sleep(random_sleep_time)

                    try:
                        img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                        element = self.driver.find_element(By.CLASS_NAME, "body-no-scroll")

                        element.click()
                        elem = self.driver.find_element(By.TAG_NAME, "html")
                        elem.send_keys(Keys.END)

                        img_elements = img_elements[3:-14]
                        for i, img in enumerate(img_elements):
                            try:
                                src = img.get_attribute('src')
                                if src:
                                    # Get the image content
                                    response = requests.get(src)

                                    if response.status_code == 200:
                                        # Construct the file path
                                        file_name = f'{full_property_address_string}__{i}.jpg'
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
            if self.floor_plan_classifer.classify_and_organise_scraped_images(): 
                floorplan_path = self.floor_plan_local_path + '\\' + full_property_address_string + '_floorplan.jpg'
                self.context.add_floor_plan_image_url(property_id, floorplan_path.strip())
                print(f"Added floorplan image url to database for {full_property_address_string}")
            
            self.move_scraped_images_to_processed_dir()
            


            
    
    def move_scraped_images_to_processed_dir(self):
        # Move the scraped images to the appropriate folders
        for file in os.listdir(self.download_dir):
            file_path = os.path.join(self.download_dir, file)
            if os.path.isfile(file_path):
                new_file_path = os.path.join(self.processed_dir, file)
                os.rename(file_path, new_file_path)

    def parse_address(self, address):
        # Split the address into components
        parts = address.split(',')

        if len(parts) >= 2:
            # Extract street address (it's the first part)
            street_address = parts[0].strip()

            # Further split the second part to separate city and state/postcode
            city_state_postcode = parts[1].split()

            # Extract city, state, and postcode
            city = ' '.join(city_state_postcode[:-2]).strip()  # City might consist of multiple words
            state_postcode = city_state_postcode[-2:]
            
            if len(state_postcode) == 2:
                state, postcode = state_postcode
            else:
                state, postcode = None, None  # In case the format is unexpected

            return street_address, city, state, postcode
        else:
            return None, None, None, None

    def close_driver(self):
        # Close the web driver
        self.driver.quit()

# Example usage:
if __name__ == "__main__":
    # Initialize the web scraper
    scraper = WebScraper()

    # URL of the website to scrape
    target_url = "https://www.domain.com.au/sale/essendon-vic-3040/?excludeunderoffer=1"

    # Collect URLs from the website
    #scraped_urls = ['https://www.domain.com.au/19-21-niagara-lane-melbourne-vic-3000-2018725443']
    scraped_urls = scraper.scrape_urls(target_url)

    # Extract photos from the collected URLs
    scraper.extract_property_information(scraped_urls)

    # Close the web driver
    scraper.close_driver()