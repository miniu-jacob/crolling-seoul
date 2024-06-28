from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

url = "https://www.deliveryk.com/shops/4221/search-products"
driver.get(url)
time.sleep(8)

try:
    cancel_button = driver.find_element(By.XPATH, "//*[text()='취소']")
    cancel_button.click()
except:
    print("링크 텍스트로 '취소' 버튼을 찾을 수 없습니다.")


# 스크롤 테스트
driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
time.sleep(3)

print("스크롤 완료")

# 브라우저 종료
driver.quit()