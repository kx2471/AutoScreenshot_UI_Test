
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from config import LOGIN_URL

def login(driver, user_id, user_pw):
    """사용자로부터 입력받은 ID와 PW로 로그인을 시도합니다."""
    if not user_id or not user_pw:
        print("ID와 PW를 모두 입력해야 합니다.")
        return False

    driver.get(LOGIN_URL)
    wait = WebDriverWait(driver, 10)

    try:
        id_field = wait.until(EC.presence_of_element_located((By.ID, 'id')))
        pw_field = wait.until(EC.presence_of_element_located((By.ID, 'pass')))

        id_field.clear()
        id_field.send_keys(user_id)
        pw_field.clear()
        pw_field.send_keys(user_pw)
        pw_field.send_keys(Keys.RETURN)

        time.sleep(3)
        
        if 'dashboard' in driver.current_url or '/' == driver.current_url[-1]:
             print("로그인 시도 성공")
             return True
        else:
            print(f"로그인 실패. 현재 URL: {driver.current_url}")
            driver.save_screenshot("login_failure.png")
            return False

    except Exception as e:
        print(f"로그인 과정에서 오류 발생: {e}")
        driver.save_screenshot("login_error.png")
        return False
