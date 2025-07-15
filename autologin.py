
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime

def login(driver, user_id, user_pw, login_url):
    """사용자로부터 입력받은 ID와 PW로 로그인을 시도합니다."""
    if not user_id or not user_pw:
        print("ID와 PW를 모두 입력해야 합니다.")
        return False

    driver.get(login_url)
    wait = WebDriverWait(driver, 10)

    try:
        id_field = wait.until(EC.presence_of_element_located((By.ID, 'id')))
        pw_field = wait.until(EC.presence_of_element_located((By.ID, 'pass')))

        id_field.clear()
        id_field.send_keys(user_id)
        pw_field.clear()
        pw_field.send_keys(user_pw)
        pw_field.send_keys(Keys.RETURN)

        try:
            # 로그인 성공 후 URL에 'dashboard'가 포함되거나 루트 URL로 돌아올 때까지 대기
            WebDriverWait(driver, 10).until(
                lambda d: 'dashboard' in d.current_url or d.current_url.endswith('/')
            )
            print("로그인 시도 성공")
            return True
        except Exception:
            print(f"로그인 실패. 현재 URL: {driver.current_url}")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            driver.save_screenshot(f"login_failure_{timestamp}.png")
            return False

    except Exception as e:
        print(f"로그인 과정에서 오류 발생: {e}")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        driver.save_screenshot(f"login_error_{timestamp}.png")
        return False
