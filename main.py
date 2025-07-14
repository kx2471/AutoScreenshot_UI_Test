import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import threading
import os

# 공용 모듈 임포트
from autologin import login
from screenshot import get_urls_from_file, capture_screenshots

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Selenium UI Test Tool - 통합 버전")
        self.root.geometry("500x400")

        self.chrome_driver = None
        self.edge_driver = None
        self.user_id = tk.StringVar()
        self.user_pw = tk.StringVar()
        self.save_path = tk.StringVar(value=os.getcwd())
        self.url_file_path = tk.StringVar(value="url.txt") # url.txt 기본값 설정

        # --- GUI 구성 ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # 로그인 정보 프레임
        login_frame = ttk.LabelFrame(main_frame, text="로그인 정보")
        login_frame.pack(fill="x", pady=5)
        ttk.Label(login_frame, text="아이디:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(login_frame, textvariable=self.user_id).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(login_frame, text="비밀번호:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Entry(login_frame, textvariable=self.user_pw, show="*").grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        login_frame.columnconfigure(1, weight=1)

        # 저장 경로 프레임
        path_frame = ttk.LabelFrame(main_frame, text="저장 경로")
        path_frame.pack(fill="x", pady=5)
        ttk.Entry(path_frame, textvariable=self.save_path, state="readonly").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Button(path_frame, text="폴더 선택", command=self.select_save_path).pack(side="right", padx=5)

        # URL 파일 경로 프레임
        url_file_frame = ttk.LabelFrame(main_frame, text="URL 파일")
        url_file_frame.pack(fill="x", pady=5)
        ttk.Entry(url_file_frame, textvariable=self.url_file_path, state="readonly").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Button(url_file_frame, text="파일 선택", command=self.select_url_file).pack(side="right", padx=5)

        # 실행 프레임
        run_frame = ttk.Frame(main_frame)
        run_frame.pack(fill="both", expand=True, pady=10)
        run_frame.columnconfigure(0, weight=1)
        run_frame.columnconfigure(1, weight=1)

        # Chrome 실행 영역
        chrome_frame = ttk.LabelFrame(run_frame, text="Chrome")
        chrome_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.chrome_login_btn = ttk.Button(chrome_frame, text="Chrome 로그인", command=lambda: self.run_login('chrome'))
        self.chrome_login_btn.pack(pady=10, fill="x", padx=10)
        self.chrome_shot_btn = ttk.Button(chrome_frame, text="Chrome 스크린샷", command=lambda: self.run_screenshot('chrome'), state="disabled")
        self.chrome_shot_btn.pack(pady=10, fill="x", padx=10)

        # Edge 실행 영역
        edge_frame = ttk.LabelFrame(run_frame, text="Edge")
        edge_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.edge_login_btn = ttk.Button(edge_frame, text="Edge 로그인", command=lambda: self.run_login('edge'))
        self.edge_login_btn.pack(pady=10, fill="x", padx=10)
        self.edge_shot_btn = ttk.Button(edge_frame, text="Edge 스크린샷", command=lambda: self.run_screenshot('edge'), state="disabled")
        self.edge_shot_btn.pack(pady=10, fill="x", padx=10)

        # 상태바
        self.status_label = ttk.Label(self.root, text="준비 완료", relief="sunken", anchor="w")
        self.status_label.pack(side="bottom", fill="x")

    def select_save_path(self):
        path = filedialog.askdirectory(initialdir=self.save_path.get())
        if path:
            self.save_path.set(path)

    def select_url_file(self):
        file_path = filedialog.askopenfilename(initialdir=os.path.dirname(self.url_file_path.get()), filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.url_file_path.set(file_path)

    def create_driver(self, browser_type):
        driver_instance = getattr(self, f"{browser_type}_driver")
        if not driver_instance:
            try:
                self.update_status(f"{browser_type.capitalize()} 드라이버 생성 중...")
                if browser_type == 'chrome':
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("excludeSwitches", ["enable-logging"])
                    options.add_argument("--start-maximized")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                    self.chrome_driver = driver
                elif browser_type == 'edge':
                    options = webdriver.EdgeOptions()
                    options.add_experimental_option("excludeSwitches", ["enable-logging"])
                    options.add_argument("--start-maximized")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
                    self.edge_driver = driver
                self.update_status(f"{browser_type.capitalize()} 드라이버 생성 완료")
                return True
            except Exception as e:
                messagebox.showerror("드라이버 오류", f"{browser_type.capitalize()} 드라이버 생성 실패: {e}")
                print(f"드라이버 생성 오류: {e}") # 콘솔에 상세 오류 출력
                return False
        return True

    def run_login(self, browser_type):
        uid = self.user_id.get()
        upw = self.user_pw.get()
        if not uid or not upw:
            messagebox.showwarning("입력 오류", "아이디와 비밀번호를 모두 입력해주세요.")
            return

        if not self.create_driver(browser_type): return

        getattr(self, f"{browser_type}_login_btn").config(state="disabled")
        threading.Thread(target=self._login_thread, args=(browser_type, uid, upw)).start()

    def _login_thread(self, browser_type, uid, upw):
        self.update_status(f"{browser_type.capitalize()} 로그인 시도 중...")
        driver = getattr(self, f"{browser_type}_driver")
        
        if login(driver, uid, upw):
            self.update_status(f"{browser_type.capitalize()} 로그인 성공")
            getattr(self, f"{browser_type}_shot_btn").config(state="normal")
        else:
            self.update_status(f"{browser_type.capitalize()} 로그인 실패")
            messagebox.showerror("로그인 실패", f"{browser_type.capitalize()} 로그인에 실패했습니다.")
            print(f"로그인 실패: {browser_type.capitalize()} 로그인 실패") # 콘솔에 상세 오류 출력
        
        getattr(self, f"{browser_type}_login_btn").config(state="normal")

    def run_screenshot(self, browser_type):
        urls = get_urls_from_file(self.url_file_path.get())
        if not urls:
            messagebox.showwarning("URL 없음", "URL 파일을 찾을 수 없거나 내용이 비어 있습니다.")
            return

        getattr(self, f"{browser_type}_shot_btn").config(state="disabled")
        threading.Thread(target=self._screenshot_thread, args=(browser_type, urls)).start()

    def _screenshot_thread(self, browser_type, urls):
        self.update_status(f"{browser_type.capitalize()} 스크린샷 캡처 중...")
        driver = getattr(self, f"{browser_type}_driver")
        
        try:
            capture_screenshots(driver, urls, self.save_path.get(), browser_type)
            self.update_status(f"{browser_type.capitalize()} 스크린샷 캡처 완료")
            messagebox.showinfo("완료", f"{browser_type.capitalize()} 스크린샷 캡처가 완료되었습니다.")
        except Exception as e:
            self.update_status(f"{browser_type.capitalize()} 스크린샷 캡처 중 오류 발생")
            messagebox.showerror("스크린샷 오류", f"{browser_type.capitalize()} 스크린샷 캡처 중 오류 발생: {e}")
            print(f"스크린샷 캡처 오류: {e}") # 콘솔에 상세 오류 출력
        finally:
            getattr(self, f"{browser_type}_shot_btn").config(state="normal")

    def update_status(self, text):
        self.status_label.config(text=text)

    def on_close(self):
        if self.chrome_driver:
            self.chrome_driver.quit()
        if self.edge_driver:
            self.edge_driver.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()