import base64
import logging
import os
import re
import time
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import get_sorted_breakpoints

def get_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        return urls
    except FileNotFoundError:
        logging.error(f"오류: {file_path} 파일을 찾을 수 없습니다.")
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
        logging.error(f"CDP 전체 페이지 스크린샷 캡처 중 오류 발생: {e}")
        try:
            driver.save_screenshot(path)
        except WebDriverException:
            logging.warning("드라이버가 이미 종료되어 스크린샷을 저장할 수 없습니다.")

def capture_screenshots(driver, urls, base_path, browser_type, breakpoints):
    if not urls:
        logging.warning("스크린샷을 캡처할 URL이 없습니다.")
        return

    # Breakpoint를 너비 기준으로 정렬 (내림차순)
    sorted_breakpoints = get_sorted_breakpoints(breakpoints)
    
    # 비동기 스크립트 타임아웃 설정 (5초)
    driver.set_script_timeout(5)

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

            for width, size_name in sorted_breakpoints:
                # 24px 오프셋을 더하여 창 크기 설정
                driver.set_window_size(width + 24, 1080)

                # requestAnimationFrame을 사용하여 렌더링이 완료될 때까지 대기
                driver.execute_async_script(
                    "const callback = arguments[arguments.length - 1];"
                    "window.requestAnimationFrame(() => {"
                    "  window.requestAnimationFrame(callback);"
                    "});"
                )

                directory = os.path.join(base_path, f"{browser_type}_{width} - {size_name}")
                if not os.path.exists(directory):
                    os.makedirs(directory)

                screenshot_path = os.path.join(directory, f"{page_title}.png")
                capture_full_page_screenshot(driver, screenshot_path)
                logging.info(f"스크린샷 저장: {screenshot_path}")
        except WebDriverException as e:
            logging.error(f"WebDriver 오류 발생: {url} 페이지 스크린샷 캡처 실패 - {e}")
            if driver:
                try:
                    driver.quit()
                except WebDriverException:
                    logging.warning("드라이버 종료 중 오류 발생 (이미 종료되었을 수 있음).")
            return # 현재 URL 스크린샷 실패 시 다음 URL로 넘어가지 않고 함수 종료
        except Exception as e:
            logging.error(f"오류 발생: {url} 페이지 스크린샷 캡처 실패 - {e}")