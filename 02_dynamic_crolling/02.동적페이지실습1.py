from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

# Chrome 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

# 알림 및 팝업 비활성화 옵션 추가
prefs = {
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.popups": 2,
    "profile.default_content_setting_values.plugins": 2
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

url = "https://www.deliveryk.com/shops/4221/search-products"
driver.get(url)

# 페이지가 완전히 로드될 시간을 충분히 줍니다
time.sleep(10)

# 팝업 취소 버튼 클릭 시도
try:
    cancel_button = driver.find_element(By.XPATH, "//*[text()='취소']")
    cancel_button.click()
except:
    print("링크 텍스트로 '취소' 버튼을 찾을 수 없습니다.")

# 스크롤 가능한 마지막 영역 찾기
scrollable_div = driver.find_element(By.CSS_SELECTOR, '.cdk-virtual-scrollable.cdk-virtual-viewport.ion-content-scroll-host')

# 현재 높이를 변수에 저장
prev_height = driver.execute_script('return arguments[0].scrollHeight', scrollable_div)

# 스크롤 동작 확인을 위한 로그 추가
print(f"초기 페이지 높이: {prev_height}")

# 스크롤 시도 횟수 제한
max_scroll_attempts = 5

# 마지막이 나타날 때까지 스크롤
scroll_attempts = 0
while scroll_attempts < max_scroll_attempts:
    scroll_attempts += 1
    # 페이지 끝까지 스크롤
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
    time.sleep(5)  # 페이지가 로드될 시간을 더 줍니다

    curr_height = driver.execute_script('return arguments[0].scrollHeight', scrollable_div)
    print(f"스크롤 시도 {scroll_attempts} - 현재 페이지 높이: {curr_height}")

    if curr_height == prev_height:
        # 페이지가 더 이상 로드되지 않으면 반페이지 정도 올렸다가 다시 스크롤
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop - arguments[0].clientHeight / 2', scrollable_div)
        time.sleep(2)
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(5)
        
        # 다시 현재 높이 확인
        new_curr_height = driver.execute_script('return arguments[0].scrollHeight', scrollable_div)
        print(f"스크롤 시도 {scroll_attempts} - 현재 페이지 높이(재확인): {new_curr_height}")

        if new_curr_height == curr_height:
            print("스크롤 완료 - 더 이상 로드할 내용이 없습니다.")
            break
        else:
            curr_height = new_curr_height

    prev_height = curr_height

print("전체 스크롤 완료")

# 페이지 소스 가져오기
html = BeautifulSoup(driver.page_source, features="html.parser")

# class 정의하여 변수에 넣기
txt_content = html.find_all(class_ = '.fs-15.fw-6.ellipsis-2.no-margin-top.ion-text-wrap')

txt_list = [i.text for i in txt_content]

# 출력 확인
for txt in txt_list:
    print(txt)

# BeautifulSoup으로 파싱

# 브라우저 종료
driver.quit()



# 과거 버전 
# driver.find_element_by_id 
# 현재 버전
# 이처럼 By 뒤에 CLASS_NAME, ID, NAME, CSS_SELECTOR, XPATH등 여러 요소들을 복사해서 이용할 수 있다. 
# driver.find_element(By.CLASS_NAME, ".Class_Name")
# driver.find_element(By.ID, "query")
# driver.find_element(By.NAME, "query").send_keys("트와이스")
# driver.find_element(By.CSS_SELECTOR, "[placeholder='검색어를 입력해 주세요.']").send_keys("에스파")
# driver.find_element(By.XPATH, 'COPIED_XPATH').send_keys("에스파")
# driver.find_element(By.LINK_TEXT, "쇼핑LIVE").click()

