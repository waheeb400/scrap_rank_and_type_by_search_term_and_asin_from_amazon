from amazoncaptcha import AmazonCaptcha
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

def find_asin_position(search_term, asin):
    url = "https://www.amazon.com"
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Handle CAPTCHA if required
    try:
        image = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div/div/form/div[1]/div/div/div[1]/img')
        image_link = image.get_attribute('src')
        captcha = AmazonCaptcha.fromlink(image_link)
        solution = captcha.solve(keep_logs=True)
        TFF = driver.find_element(By.XPATH, '//*[@id="captchacharacters"]')
        TFF.send_keys(solution)
        button = driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/div/div/form/div[2]/div/span/span/button')
        button.click()
    except Exception as e:
        print("No CAPTCHA or CAPTCHA handling failed:", e)

    # Search for the given search term
    try:
        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='twotabsearchtextbox']"))
        )
        search_bar.send_keys(search_term)
        search_bar.send_keys(Keys.RETURN)
        time.sleep(5)
        page_source = driver.page_source
    finally:
        driver.quit()

    # Extract search results and find the ASIN's position
    soup = BeautifulSoup(page_source, 'html.parser')
    asin_positions = []
    for index, result in enumerate(soup.find_all('div', {'data-asin': True}), start=1):
        result_asin = result['data-asin']
        if result_asin == asin:
            if "Sponsored" in result.get_text():
                position_info = {'position': index, 'type': 'Sponsored'}
            else:
                position_info = {'position': index, 'type': 'Natural'}
            asin_positions.append(position_info)

    return asin_positions
def main():
    search = 'mouse trap'
    asin = 'B07QCCQT7H'
    positions = find_asin_position(search, asin)
    if positions:
        for position_info in positions:
            position = position_info['position']
            position_type = position_info['type']
            print(f"ASIN {asin} was found at position: {position}, Type: {position_type}")
    else:
        print(f"ASIN {asin} was not found in the search results.")

if __name__ == "__main__":
    main()
