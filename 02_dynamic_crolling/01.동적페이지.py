from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup

driver_path = "D:\\projects\\miniu\\crolling\\chromedriver-win64\\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(executable_path=driver_path)

url = 'https://www.deliveryk.com/shops/4221/search-products'
driver.get(url)

time.sleep(10)
try:
    cancel_button = driver.find_element(By.XPATH, "//*[text()='취소']")
    cancel_button.click()
except:
    print("링크 텍스트로 '취소' 버튼을 찾을 수 없습니다.")

driver.find_element(By.XPATH, value = '/html/body/app-root/ion-app/ion-router-outlet/app-search-products/ion-content/div/cdk-virtual-scroll-viewport/div[1]/div[2]/div/app-product-cart-item/div/ion-item/ion-label/h2').click()
