import json
import logging
import os
import platform  # OS 감지를 위해 추가
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService

# 공용 모듈 임포트
from autologin import login
from screenshot import capture_screenshots, get_urls_from_file
from compare_screenshots import run_comparison

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Selenium UI Test Tool - 통합 버전")
        self.root.geometry("600x600")

        self.chrome_driver = None
        self.edge_driver = None
        self.safari_driver = None # Safari 드라이버 속성 추가
        self.user_id = tk.StringVar()
        self.user_pw = tk.StringVar()
        self.save_path = tk.StringVar(value=os.getcwd())
        self.url_file_path = tk.StringVar(value="url.txt") # url.txt 기본값 설정
        
        # config.py에서 기본값 로드
        from config import DEFAULT_LOGIN_URL, DEFAULT_BREAKPOINTS
        self.login_url = tk.StringVar(value=DEFAULT_LOGIN_URL)
        
        # Breakpoint 설정을 위한 StringVar. 딕셔너리를 문자열로 저장
        self.breakpoints_config = tk.StringVar(value=json.dumps(DEFAULT_BREAKPOINTS)) 

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

        # 로그인 URL 설정 프레임
        login_url_frame = ttk.LabelFrame(main_frame, text="로그인 URL")
        login_url_frame.pack(fill="x", pady=5)
        ttk.Entry(login_url_frame, textvariable=self.login_url).pack(side="left", fill="x", expand=True, padx=5, pady=5)

        # Breakpoint 설정 프레임
        breakpoint_frame = ttk.LabelFrame(main_frame, text="Breakpoint 설정")
        breakpoint_frame.pack(fill="x", pady=5)
        ttk.Entry(breakpoint_frame, textvariable=self.breakpoints_config, state="readonly").pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ttk.Button(breakpoint_frame, text="편집", command=self.edit_breakpoints).pack(side="right", padx=5)

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

        # 실행 프레임 (동적으로 브라우저 버튼 생성)
        run_frame = ttk.Frame(main_frame)
        run_frame.pack(fill="both", expand=True, pady=10)
        
        # 지원할 브라우저 목록 설정
        browsers = ['chrome', 'edge']
        if platform.system() == 'Darwin': # macOS일 경우 Safari 추가
            browsers.append('safari')

        # 각 브라우저에 대한 버튼 동적 생성
        for i, browser_name in enumerate(browsers):
            run_frame.columnconfigure(i, weight=1)
            
            browser_frame = ttk.LabelFrame(run_frame, text=browser_name.capitalize())
            browser_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            login_btn = ttk.Button(browser_frame, text=f"{browser_name.capitalize()} 로그인", command=lambda b=browser_name: self.run_login(b))
            login_btn.pack(pady=10, fill="x", padx=10)
            setattr(self, f"{browser_name}_login_btn", login_btn)

            shot_btn = ttk.Button(browser_frame, text=f"{browser_name.capitalize()} 스크린샷", command=lambda b=browser_name: self.run_screenshot(b), state="disabled")
            shot_btn.pack(pady=10, fill="x", padx=10)
            setattr(self, f"{browser_name}_shot_btn", shot_btn)

        # 비교 실행 프레임
        compare_frame = ttk.LabelFrame(main_frame, text="비교 실행")
        compare_frame.pack(fill="x", pady=5)
        self.compare_btn = ttk.Button(compare_frame, text="스크린샷 비교 실행", command=self.run_comparison_thread)
        self.compare_btn.pack(pady=10, fill="x", padx=10)

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

    def edit_breakpoints(
        self
    ):
        # Breakpoint 편집을 위한 새 Toplevel 윈도우 생성
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Breakpoint 편집")
        
        from config import BREAKPOINT_VALID_RANGES # 유효 범위 가져오기

        # 현재 설정된 Breakpoint 값을 가져와서 딕셔너리로 변환
        try:
            current_breakpoints = json.loads(self.breakpoints_config.get())
        except json.JSONDecodeError:
            current_breakpoints = {}

        # Breakpoint 항목들을 저장할 리스트
        breakpoint_entries = []

        # 각 Breakpoint 항목을 표시하고 편집할 수 있도록 구성
        for i, (name, width) in enumerate(current_breakpoints.items()):
            frame = ttk.Frame(edit_window)
            frame.pack(fill="x", padx=5, pady=2)

            ttk.Label(frame, text="해상도:").pack(side="left")
            ttk.Label(frame, text=name, width=10).pack(side="left", padx=2)

            ttk.Label(frame, text="너비:").pack(side="left")
            width_entry = ttk.Entry(frame, width=10)
            width_entry.insert(0, str(width))
            width_entry.pack(side="left", padx=2)

            # 유효 범위 표시
            range_text = ""
            if name in BREAKPOINT_VALID_RANGES:
                min_w, max_w = BREAKPOINT_VALID_RANGES[name]
                if max_w is None: # XL의 경우
                    range_text = f"({min_w} 이상)"
                else:
                    range_text = f"({min_w}~{max_w})"
            ttk.Label(frame, text=range_text, width=15).pack(side="left", padx=2)
            
            breakpoint_entries.append((name, width_entry))

        def save_breakpoints():
            new_breakpoints = {}
            from config import BREAKPOINT_VALID_RANGES # 유효 범위 가져오기
            # current_breakpoints의 키(이름)를 사용하고, width_entry에서 값 가져오기
            for i, (name, _) in enumerate(current_breakpoints.items()):
                width_entry = breakpoint_entries[i][1] # width_entry만 가져옴
                width_str = width_entry.get().strip()
                if width_str.isdigit():
                    width = int(width_str)
                    # 유효성 검사 추가
                    if name in BREAKPOINT_VALID_RANGES:
                        min_width, max_width = BREAKPOINT_VALID_RANGES[name]
                        if not (min_width <= width <= max_width):
                            messagebox.showwarning("입력 오류", f"'{name}' Breakpoint의 너비({width})가 유효 범위({min_width}~{max_w}) 밖에 있습니다.")
                            return
                    new_breakpoints[name] = width
                else:
                    messagebox.showwarning("입력 오류", f"'{name}' Breakpoint의 너비가 유효한 숫자가 아닙니다.")
                    return
            
            self.breakpoints_config.set(json.dumps(new_breakpoints))
            edit_window.destroy()

        ttk.Button(edit_window, text="저장", command=save_breakpoints).pack(pady=10)

    def create_driver(self, browser_type):
        driver_instance = getattr(self, f"{browser_type}_driver", None)
        if not driver_instance:
            try:
                self.update_status(f"{browser_type.capitalize()} 드라이버 생성 중...")
                if browser_type == 'chrome':
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("excludeSwitches", ["enable-logging"])
                    options.add_argument("--start-maximized")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(options=options)
                    self.chrome_driver = driver
                elif browser_type == 'edge':
                    # Edge는 Windows에서만 실행 가능하다고 가정
                    if platform.system() != 'Windows':
                        messagebox.showerror("OS 오류", "Edge는 Windows에서만 사용할 수 있습니다.")
                        return False
                    edge_driver_path = os.path.join(os.getcwd(), "msedgedriver.exe")
                    if not os.path.exists(edge_driver_path):
                        messagebox.showerror("드라이버 오류", f"Edge 드라이버를 찾을 수 없습니다.\n경로: {edge_driver_path}")
                        return False
                    service = EdgeService(executable_path=edge_driver_path)
                    options = webdriver.EdgeOptions()
                    options.add_experimental_option("excludeSwitches", ["enable-logging"])
                    options.add_argument("--start-maximized")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    driver = webdriver.Edge(service=service, options=options)
                    self.edge_driver = driver
                elif browser_type == 'safari':
                    # Safari는 macOS에서만 실행 가능
                    if platform.system() != 'Darwin':
                        messagebox.showerror("OS 오류", "Safari는 macOS에서만 사용할 수 있습니다.")
                        return False
                    driver = webdriver.Safari()
                    self.safari_driver = driver
                
                self.update_status(f"{browser_type.capitalize()} 드라이버 생성 완료")
                return True
            except Exception as e:
                messagebox.showerror("드라이버 오류", f"{browser_type.capitalize()} 드라이버 생성 실패: {e}")
                logging.error(f"드라이버 생성 오류: {e}")
                return False
        else:
            logging.info(f"{browser_type.capitalize()} 드라이버가 이미 생성되어 있습니다.")
            return True

    def run_login(self, browser_type):
        uid = self.user_id.get()
        upw = self.user_pw.get()
        login_url = self.login_url.get()
        
        if not uid or not upw:
            messagebox.showwarning("입력 오류", "아이디와 비밀번호를 모두 입력해주세요.")
            return
        
        if not login_url:
            messagebox.showwarning("입력 오류", "로그인 URL을 입력해주세요.")
            return

        if not self.create_driver(browser_type): return

        getattr(self, f"{browser_type}_login_btn").config(state="disabled")
        threading.Thread(target=self._login_thread, args=(browser_type, uid, upw, login_url)).start() 

    def _login_thread(self, browser_type, uid, upw, login_url): 
        self.update_status(f"{browser_type.capitalize()} 로그인 시도 중...")
        driver = getattr(self, f"{browser_type}_driver")
        
        if login(driver, uid, upw, login_url): 
            self.update_status(f"{browser_type.capitalize()} 로그인 성공")
            getattr(self, f"{browser_type}_shot_btn").config(state="normal")
        else:
            self.update_status(f"{browser_type.capitalize()} 로그인 실패")
            messagebox.showerror("로그인 실패", f"{browser_type.capitalize()} 로그인에 실패했습니다.")
            logging.error(f"로그인 실패: {browser_type.capitalize()} 로그인 실패")
        
        getattr(self, f"{browser_type}_login_btn").config(state="normal")

    def run_screenshot(self, browser_type):
        urls = get_urls_from_file(self.url_file_path.get())
        if not urls:
            messagebox.showwarning("URL 없음", "URL 파일을 찾을 수 없거나 내용이 비어 있습니다.")
            return
        
        try:
            breakpoints = json.loads(self.breakpoints_config.get())
            if not isinstance(breakpoints, dict):
                raise ValueError("Breakpoint 설정이 올바른 딕셔너리 형식이 아닙니다.")
        except Exception as e:
            messagebox.showerror("설정 오류", f"Breakpoint 설정 파싱 오류: {e}")
            return

        getattr(self, f"{browser_type}_shot_btn").config(state="disabled")
        threading.Thread(target=self._screenshot_thread, args=(browser_type, urls, breakpoints)).start() 

    def _screenshot_thread(self, browser_type, urls, breakpoints): 
        self.update_status(f"{browser_type.capitalize()} 스크린샷 캡처 중...")
        driver = getattr(self, f"{browser_type}_driver")
        
        try:
            capture_screenshots(driver, urls, self.save_path.get(), browser_type, breakpoints) 
            self.update_status(f"{browser_type.capitalize()} 스크린샷 캡처 완료")
            messagebox.showinfo("완료", f"{browser_type.capitalize()} 스크린샷 캡처가 완료되었습니다.")
        except Exception as e:
            self.update_status(f"{browser_type.capitalize()} 스크린샷 캡처 중 오류 발생")
            messagebox.showerror("스크린샷 오류", f"{browser_type.capitalize()} 스크린샷 캡처 중 오류 발생: {e}")
            logging.error(f"스크린샷 캡처 오류: {e}")
        finally:
            getattr(self, f"{browser_type}_shot_btn").config(state="normal")

    def run_comparison_thread(self):
        self.update_status("스크린샷 비교 시작...")
        self.compare_btn.config(state="disabled")
        threading.Thread(target=self._run_comparison).start()

    def _run_comparison(self):
        base_path = self.save_path.get()
        try:
            diff_count, output_path = run_comparison(base_path)
            self.update_status(f"비교 완료. 총 {diff_count}개의 차이점 발견.")
            if diff_count > 0:
                messagebox.showinfo("비교 완료", f"총 {diff_count}개의 차이점을 발견했습니다.\n결과가 저장된 폴더: {output_path}")
            else:
                messagebox.showinfo("비교 완료", "차이점을 발견하지 못했습니다.")
        except Exception as e:
            self.update_status("비교 중 오류 발생")
            messagebox.showerror("비교 오류", f"스크린샷 비교 중 오류 발생: {e}")
            logging.error(f"스크린샷 비교 오류: {e}")
        finally:
            self.compare_btn.config(state="normal")

    def update_status(self, text):
        self.status_label.config(text=text)

    def on_close(self):
        if self.chrome_driver:
            self.chrome_driver.quit()
        if self.edge_driver:
            self.edge_driver.quit()
        if self.safari_driver: # Safari 드라이버 종료 추가
            self.safari_driver.quit()
        self.root.destroy()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
