import os
import requests
from pyairtable import Api
from pyairtable.formulas import match

# Airtable 설정
AIRTABLE_API_KEY = 'YOUR API KEY'
BASE_ID = 'appINqW1EtwrFL5gp'
TABLE_NAME = 'tblDDRGv8LbYOTMDd'

# Airtable API 객체 생성 및 테이블 참조
api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, TABLE_NAME)

# 이미지를 다운로드할 디렉토리 설정
download_dir = "downloaded_images"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# 모든 레코드 가져오기
records = table.all()

# 파일명에서 사용할 수 없는 문자를 대체하는 함수
def sanitize_filename(filename):
    return "".join(c if c.isalnum() else "_" for c in filename)

# 레코드 처리
for record in records:
    product_name = record['fields'].get('Product Name')
    image_url = record['fields'].get('URL')
    image_field_name = 'Image'

    if not image_url:
        print(f"{product_name}에 URL이 없습니다. 다음 항목으로 넘어갑니다.")
        continue

    # 이미지 다운로드
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_data = response.content
        sanitized_product_name = sanitize_filename(product_name)
        image_filename = os.path.join(download_dir, f"{sanitized_product_name}.jpg")
        
        with open(image_filename, 'wb') as image_file:
            image_file.write(image_data)
        print(f"{product_name}의 이미지를 다운로드했습니다.")

        # Airtable에 이미지 첨부
        try:
            table.update(record['id'], {
                image_field_name: [{'url': image_url}]
            })
            print(f"{product_name}의 이미지를 Airtable에 첨부했습니다.")
        except Exception as e:
            print(f"{product_name}의 이미지를 Airtable에 첨부하는 도중 오류 발생: {e}")

    except requests.RequestException as e:
        print(f"{product_name}의 이미지를 다운로드하는 도중 오류 발생: {e}")
    except Exception as e:
        print(f"{product_name}의 이미지를 Airtable에 첨부하는 도중 오류 발생: {e}")