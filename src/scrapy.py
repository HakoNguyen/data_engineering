from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd


options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service("chromedriver_win64/chromedriver.exe"), options=options)
driver.get("https://books.toscrape.com/")

books_data = []

while True:
    books = driver.find_elements(By.XPATH, "//h3/a")
    for book in books: 
        link = book.get_attribute("href")

        driver.execute_script("window.open(arguments[0]);", link)
        driver.switch_to.window(driver.window_handles[1])

        try:
            title = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            ).text

            category = driver.find_element(By.XPATH, '//ul[@class="breadcrumb"]/li[3]/a').text

            price = driver.find_element(By.CLASS_NAME, "price_color").text

            try: 
                description_header = driver.find_element(By.ID, "product_description")
                description = description_header.find_element(By.XPATH, "following-sibling::p").text

            except NoSuchElementException:
                description = "N/A"

            try:
                rating = driver.find_element(By.XPATH, "//p[contains(@class, 'star-rating')]").get_attribute("class").split()[-1]
            except NoSuchElementException:
                rating = "N/A"

            books_data.append({
                "title": title,
                "product_type":  category,
                "price": price,
                "description": description,
                "rating": rating
            })
            print(f"✅ Lấy xong: {title}")

        except TimeoutError:
            print(f"Timeout")
            
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    try:
        next_button = driver.find_element(By.XPATH, '//li[@class="next"]/a')
        next_button.click()
    except NoSuchElementException:
        break

driver.quit()        


df = pd.DataFrame(books_data)

df.to_csv("data/books_data.csv", index=False, encoding="utf-8-sig")