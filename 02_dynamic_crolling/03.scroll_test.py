import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pyairtable import Api

# Airtable 설정
AIRTABLE_API_KEY = 'pat6wyIJ4QYHYY2Yd.55e5bb1a07d8883a8bdfa02a779aed612a0f800c8f252c17a12dac34a4e2347b'
BASE_ID = 'appINqW1EtwrFL5gp'
TABLE_NAME = 'tblDDRGv8LbYOTMDd'

# Airtable API 객체 생성 및 테이블 참조
api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, TABLE_NAME)

# driver_path에 파일이 있는지 확인
driver_path = "D:\\projects\\miniu\\chromedriver-win64\\chromedriver.exe"
if not os.path.exists(driver_path):
    print(f"ChromeDriver가 '{driver_path}' 경로에 존재하지 않습니다. 프로그램을 종료합니다.")
    exit()

# Airtable 접근 확인 및 샘플 데이터 삽입
try:
    sample_data = {
        "Product Name": "진로 이즈 백 1박스",
        "Price": 1180000,  # Price를 숫자 형식으로 변경
        "URL": "https://d3i25w97yl4le9.cloudfront.net/thumb/products/LnwUidPyML9PTyR3mjJnJHvrOuO3MzQhgOXYQVJJ.jpg"
    }
    sample_record = table.create(sample_data)
    print("Airtable에 접근 및 샘플 데이터 삽입 성공")
    
    # 2초 후 샘플 데이터 삭제
    time.sleep(4)
    table.delete(sample_record['id'])
    print("샘플 데이터 삭제 성공")
except Exception as e:
    print(f"Airtable 접근 또는 샘플 데이터 삽입 중 오류 발생: {e}")
    exit()

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

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

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

# 전체 데이터를 저장할 리스트
all_products = []

# 페이지수를 체크하기 위한 변수
page_count = 0
max_pages = 2
max_retries = 3  # 최대 재시도 횟수

def get_image_url(element):
    try:
        shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
        if shadow_root:
            img_element = shadow_root.find_element(By.CSS_SELECTOR, 'img')
            return img_element.get_attribute('src')
        else:
            print(f"Shadow root가 비어 있습니다. Element: {element.get_attribute('outerHTML')}")
            return None
    except Exception as e:
        print(f"이미지 URL을 가져오는 도중 오류 발생: {e}")
        print(f"문제가 발생한 element: {element.get_attribute('outerHTML')}")
        return None

def extract_data():
    html = BeautifulSoup(driver.page_source, "html.parser")
    products = html.select('h2.fs-15.fw-6.ellipsis-2.no-margin-top.ion-text-wrap')
    prices = html.select('.fs-14.ion-color.ion-color-dark.md.hydrated')
    images = driver.find_elements(By.CSS_SELECTOR, 'ion-img.center-crop.md.hydrated')
    print(f"현재 페이지에서 찾은 제품 수: {len(products)}, 가격 수: {len(prices)}, 이미지 수: {len(images)}")
    
    page_products = []
    for product, price, image_element in zip(products, prices, images):
        product_name = product.get_text(strip=True)
        price_text = int(''.join(filter(str.isdigit, price.get_text(strip=True))))  # 가격을 숫자 형식으로 변환
        image_url = get_image_url(image_element)  # 이미지 URL 추출
        page_products.append((product_name, price_text, image_url))
        all_products.append((product_name, price_text, image_url))
    
    return page_products, products

# 첫 번째 페이지의 데이터를 가져와서 리스트에 추가
page_products, _ = extract_data()
print(f"첫 페이지 데이터를 가져왔습니다. 데이터 수: {len(page_products)}")

# 페이지수를 체크하며 최대 2페이지까지 스크롤
while page_count < max_pages:
    retries = 0
    while retries < max_retries:
        # 한 페이지씩 스크롤
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].clientHeight', scrollable_div)
        time.sleep(10)  # 페이지가 로드될 시간을 더 줍니다

        page_products, products = extract_data()
        if len(page_products) > 0:
            print(f"페이지 {page_count + 1} 데이터를 가져왔습니다. 데이터 수: {len(page_products)}")
            break
        else:
            print(f"페이지 {page_count + 1} 데이터를 가져오지 못했습니다. 재시도: {retries + 1}")
            retries += 1

    page_count += 1

print("전체 스크롤 완료")

# 마지막 페이지에서 누락된 URL을 다시 시도
last_page_retries = 2
for _ in range(last_page_retries):
    missing_url_items = [(product_name, price_text, image_url) for product_name, price_text, image_url in all_products if image_url is None]
    if not missing_url_items:
        break
    print(f"마지막 페이지에서 {len(missing_url_items)}개의 누락된 URL을 다시 시도합니다.")
    
    time.sleep(3)
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop - arguments[0].clientHeight / 2', scrollable_div)
    time.sleep(2)
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
    time.sleep(5)
    
    html = BeautifulSoup(driver.page_source, "html.parser")
    products = html.select('h2.fs-15.fw-6.ellipsis-2.no-margin-top.ion-text-wrap')
    prices = html.select('.fs-14.ion-color.ion-color-dark.md.hydrated')
    images = driver.find_elements(By.CSS_SELECTOR, 'ion-img.center-crop.md.hydrated')

    for product_name, price_text, _ in missing_url_items:
        try:
            product = next(p for p in products if p.get_text(strip=True) == product_name)
            price = next(pr for pr in prices if ''.join(filter(str.isdigit, pr.get_text(strip=True))) == price_text)
            image_element = next(img for img in images if driver.execute_script('return arguments[0].shadowRoot.querySelector("img").src', img) is not None)
            image_url = get_image_url(image_element)
            for i, (pn, pt, iu) in enumerate(all_products):
                if pn == product_name and pt == price_text and iu is None:
                    all_products[i] = (pn, pt, image_url)
                    break
        except StopIteration:
            continue

# 중복 제거 (URL이 있는 항목을 우선으로)
unique_products = {}
for product_name, price_text, image_url in all_products:
    if product_name not in unique_products or (unique_products[product_name][1] is None and image_url is not None):
        unique_products[product_name] = (price_text, image_url)

# Airtable에 데이터 추가
for product_name, (price_text, image_url) in unique_products.items():
    try:
        table.create({
            "Product Name": product_name,
            "Price": price_text,
            "URL": image_url
        })
    except Exception as e:
        print(f"Airtable에 데이터를 추가하는 도중 오류 발생: {e}")

# 텍스트 리스트 생성 및 출력
for idx, (product_name, (price_text, image_url)) in enumerate(unique_products.items(), 1):
    print(f"{idx}. 상품명: {product_name}, 가격: {price_text}, URL: {image_url}")

# 브라우저 종료
# driver.quit()
