
import os
import time
import re
import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from config import BREAKPOINTS

def get_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"오류: {file_path} 파일을 찾을 수 없습니다.")
        return []

def capture_full_page_screenshot(driver, path):
    try:
        page_rect = driver.execute_cdp_cmd('Page.getLayoutMetrics', {})
        screenshot_config = {
            'captureBeyondViewport': True,
            'fromSurface': True,
            'clip': {
                'width': page_rect['cssContentSize']['width'],
                'height': page_rect['cssContentSize']['height'],
                'x': 0,
                'y': 0,
                'scale': 1
            },
        }
        base64_png = driver.execute_cdp_cmd('Page.captureScreenshot', screenshot_config)
        bytes_data = base64.urlsafe_b64decode(base64_png['data'])
        with open(path, "wb") as f:
            f.write(bytes_data)
    except Exception as e:
        print(f"CDP 전체 페이지 스크린샷 캡처 중 오류 발생: {e}")
        driver.save_screenshot(path)

def capture_screenshots(driver, urls, base_path, browser_type):
    if not urls:
        print("스크린샷을 캡처할 URL이 없습니다.")
        return

    for url in urls:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            parsed_url = urlparse(url)
            path_segments = [segment for segment in parsed_url.path.split('/') if segment]
            
            if path_segments:
                base_name = path_segments[-1]
            else:
                base_name = "home"
            
            if parsed_url.query:
                base_name += "_" + re.sub(r'[?&=]', '_', parsed_url.query)

            page_title = re.sub(r'[^a-zA-Z0-9_.-]', '', base_name) # 파일명으로 부적합한 문자 제거

            for width, size_name in BREAKPOINTS.items():
                driver.set_window_size(width, 1080)
                time.sleep(1)

                directory = os.path.join(base_path, f"{browser_type}_{width} - {size_name}")
                if not os.path.exists(directory):
                    os.makedirs(directory)

                screenshot_path = os.path.join(directory, f"{page_title}.png")
                capture_full_page_screenshot(driver, screenshot_path)
                print(f"스크린샷 저장: {screenshot_path}")
        except Exception as e:
            print(f"오류 발생: {url} 페이지 스크린샷 캡처 실패 - {e}")
