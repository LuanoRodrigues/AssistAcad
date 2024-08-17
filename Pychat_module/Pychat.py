from logging.handlers import TimedRotatingFileHandler
import subprocess
import win32api
from alive_progress import alive_bar, alive_it,config_handler
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as SeleniumExceptions
from selenium.webdriver.support.ui import WebDriverWait
from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
import win32gui
import win32con
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pyautogui

pyautogui.FAILSAFE = False

timeout = 300

import undetected_chromedriver as uc
from markdownify import markdownify
from threading import Thread
import platform
import logging
import weakref
import json
import time
import re
import os
import pyperclip

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

cf_challenge_form = (By.ID, 'challenge-form')

chatgpt_textbox = (By.TAG_NAME, 'textarea')
chatgpt_streaming = (By.CLASS_NAME, 'result-streaming')
chatgpt_big_response = (By.XPATH, '//div[@class="flex-1 overflow-hidden"]//div[p]')
chatgpt_small_response = (
    By.XPATH,
    '//div[starts-with(@class, "markdown prose w-full break-words")]',
)
chatgpt_alert = (By.XPATH, '//div[@role="alert"]')
chatgpt_intro = (By.ID, 'headlessui-portal-root')
chatgpt_login_btn = (By.XPATH, '//button[text()="Log in"]')
chatgpt_login_h1 = (By.XPATH, '//h1[text()="Welcome back"]')
chatgpt_logged_h1 = (By.XPATH, '//h1[text()="ChatGPT"]')

chatgpt_chats_list_first_node = (
    By.XPATH,
    '//div[substring(@class, string-length(@class) - string-length("text-sm") + 1)  = "text-sm"]//a',
)

chatgpt_chat_url = 'https://chat.openai.com/chat'


class ChatGPT:
    def __init__(
            self,
            session_token: str = None,
            conversation_id: str = '',
            chat_id: str = None,
            auth_type: str = None,
            login_cookies_path: str = '',
            captcha_solver: str = 'pypasser',
            solver_apikey: str = '',
            proxy: str = None,
            chrome_args: list = [],
            moderation: bool = True,
            verbose: bool = False,
            check_url: bool = True,
            os: str = 'win',


    ):
        '''
        Initialize the ChatGPT object\n
        :param session_token: The session token to use for authentication
        :param conversation_id: The conversation ID to use for the chat session
        :param auth_type: The authentication type to use (`google`, `microsoft`, `openai`)
        :param login_cookies_path: The path to the cookies file to use for authentication
        :param captcha_solver: The captcha solver to use (`pypasser`, `2captcha`)
        :param solver_apikey: The apikey of the captcha solver to use (if any)
        :param proxy: The proxy to use for the browser (`https://ip:port`)
        :param chrome_args: The arguments to pass to the browser
        :param moderation: Whether to enable message moderation
        :param verbose: Whether to enable verbose logging
        '''
        self.__init_logger(verbose)

        self.__session_token = session_token
        self.__conversation_id = conversation_id
        self.chat_id = chat_id
        self.__auth_type = auth_type
        self.__login_cookies_path = login_cookies_path
        self.__captcha_solver = captcha_solver
        self.__solver_apikey = solver_apikey
        self.__proxy = proxy
        self.__chrome_args = chrome_args
        self.__moderation = moderation
        self.finalize = weakref.finalize(self, self.__del__)
        self.url = ""
        self.current = ""
        self.check_url = check_url
        self.os = os

        if not self.__session_token and (
                not self.__auth_type
        ):
            raise ValueError(
                'Please provide either a session token or login credentials'
            )
        if self.__auth_type not in [None, 'google', 'microsoft', 'openai']:
            raise ValueError('Invalid authentication type')
        if self.__captcha_solver not in [None, 'pypasser', '2captcha']:
            raise ValueError('Invalid captcha solver')
        if self.__captcha_solver == '2captcha' and not self.__solver_apikey:
            raise ValueError('Please provide a 2captcha apikey')
        if self.__proxy and not re.findall(
                r'(https?|socks(4|5)?):\/\/.+:\d{1,5}', self.__proxy
        ):
            raise ValueError('Invalid proxy format')
        if self.__auth_type == 'openai' and self.__captcha_solver == 'pypasser':
            try:
                import ffmpeg_downloader as ffdl
            except ModuleNotFoundError:
                raise ValueError(
                    'Please install ffmpeg_downloader, PyPasser, and pocketsphinx by running `pip install ffmpeg_downloader PyPasser pocketsphinx`'
                )

            ffmpeg_installed = bool(ffdl.ffmpeg_version)
            self.logger.debug(f'ffmpeg installed: {ffmpeg_installed}')
            if not ffmpeg_installed:
                import subprocess

                subprocess.run(['ffdl', 'install'])
            os.environ['PATH'] += os.pathsep + ffdl.ffmpeg_dir

        self.__init_browser()

    def __del__(self):
        '''
        Close the browser and display
        '''
        self.__is_active = False
        if hasattr(self, 'driver'):
            self.logger.debug('Closing browser...')
            self.driver.quit()
        if hasattr(self, 'display'):
            self.logger.debug('Closing display...')
            self.display.stop()

    def __init_logger(self, verbose: bool, log_file='logfile.log') -> None:
        '''
        Initialize the logger\n
        :param verbose: Whether to enable verbose logging
        '''
        self.logger = logging.getLogger('pyChatGPT')
        self.logger.setLevel(logging.DEBUG)
        if verbose:
            formatter = logging.Formatter('[%(funcName)s] %(message)s')
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

            # Create a TimedRotatingFileHandler to write logs to a file
            file_handler = TimedRotatingFileHandler(log_file, when='S', interval=99999999, backupCount=1)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def __init_browser(self) -> None:
        '''
        Initialize the browser
        '''

        self.logger.debug('Initializing browser...')
        # Calculate the height
        height = int(2 / 3 * 1024)  # 2/3 of 1024
        options = uc.ChromeOptions()
        # Set the window size
        options.add_argument(f'--window-size=1024,{height}')
        # options.add_argument(self.profile_path)
        if self.os == "win":
            options.add_argument("--user-data-dir=C:\\Users\\luano\\AppData\\Local\\Google\\Chrome\\User Data")
            options.add_argument("--profile-directory=Profile 2")
        if self.os=='mac':
            options.add_argument("--profile-directory=Profile 1")
        # options.add_argument("--incognito")
        # options.add_argument('--window-size=1024,568')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,  # Block notifications
            "profile.default_content_setting_values.popups": 2,  # Block pop-ups
        })

        if self.__proxy:
            options.add_argument(f'--proxy-server={self.__proxy}')
        for arg in self.__chrome_args:
            options.add_argument(arg)
        try:

            self.driver = uc.Chrome( options=options)


        except TypeError as e:
            if str(e) == 'expected str, bytes or os.PathLike object, not NoneType':
                raise ValueError('Chrome installation not found')
            raise e

        if self.__login_cookies_path and os.path.exists(self.__login_cookies_path):
            self.logger.debug('Restoring cookies...')
            try:
                with open(self.__login_cookies_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    if cookie['name'] == '__Secure-next-auth.session-token':
                        self.__session_token = cookie['value']
            except json.decoder.JSONDecodeError:
                self.logger.debug(f'Invalid cookies file: {self.__login_cookies_path}')

        if self.__session_token:
            self.logger.debug('Restoring session_token...')
            self.driver.execute_cdp_cmd(
                'Network.setCookie',
                {
                    'domain': 'chat.openai.com',
                    'path': '/',
                    'name': '__Secure-next-auth.session-token',
                    'value': self.__session_token,
                    'httpOnly': True,
                    'secure': True,
                },
            )

        if not self.__moderation:
            self.logger.debug('Blocking moderation...')
            self.driver.execute_cdp_cmd(
                'Network.setBlockedURLs',
                {'urls': ['https://chat.openai.com/backend-api/moderations']},
            )

        self.logger.debug('Ensuring Cloudflare cookies...')
        self.__ensure_cf()

        self.logger.debug('Opening chat page...')
        if self.chat_id:
            if self.chat_id == "consensus":
                self.chat_id = "/g/g-bo0FiWLY7-consensus"
            if self.chat_id =="o":
                self.chat_id = "?model=gpt-4o"
            if self.chat_id == "Statements Database":
                self.chat_id = "/g/g-zc9XeRbjL"
            if self.chat_id == "summary":
                self.chat_id = "/g/g-PM8cJsFgY-academic-summary-assistant"
            if self.chat_id == "meu":
                self.chat_id = "/g/g-8dBHrjLA4"
                # self.chat_id="/gpts/editor/g-8dBHrjLA4"
            if self.chat_id == "evaluator":
                self.chat_id = "/g/g-R5g8dbYOl-assignment-evaluator"
            if self.chat_id == "4":
                self.chat_id = "?model=gpt-4"
            if self.chat_id == "scholar":
                self.chat_id = "/g/g-kZ0eYXlJe-scholar-gpt"
            if self.chat_id == "scispace":
                self.chat_id = "/g/g-NgAcklHd8-scispace"
            if self.chat_id == "askpdf":
                self.chat_id = "/g/g-UfFxTDMxq-askyourpdf-research-assistant"
            if self.chat_id == "lit":
                self.chat_id = "/g/g-lfY2IC1TZ-auto-literature-review"

            if self.chat_id == "pdf":
                self.chat_id = "/g/g-l3aJUSU8K-ask-pdf"

            if self.chat_id == "":
                self.driver.get(f'https://chat.openai.com')
            self.url = f'https://chat.openai.com{self.chat_id}?temporary-chat=true'

            # self.url = f'https://chat.openai.com/{self.chat_id}'
            self.driver.get(self.url)
        else:
            self.driver.get(f'{chatgpt_chat_url}/{self.__conversation_id}')
        self.__check_blocking_elements()

        self.__is_active = True
        Thread(target=self.__keep_alive, daemon=True).start()

    def is_file_dialog_open(self, filename="",insert=True):
        def enum_windows_proc(hwnd, lParam):
            class_name = win32gui.GetClassName(hwnd)
            if class_name == '#32770':  # Class name for dialogs
                title = win32gui.GetWindowText(hwnd)
                if "Open" in title or "Save" in title or "Select" in title:
                    lParam.append(hwnd)
            return True

        open_dialogs = []
        win32gui.EnumWindows(enum_windows_proc, open_dialogs)
        if insert==False:
            return open_dialogs
        if open_dialogs:
            dialog_hwnd = open_dialogs[0]
            try:
                app = Application().connect(handle=dialog_hwnd)
                dialog = app.window(handle=dialog_hwnd)

                # self.logger.debug control identifiers to inspect the dialog
                # dialog.self.logger.debug_control_identifiers()

                # Find the ComboBox and then the Edit control within it
                combo_box = dialog.child_window(class_name="ComboBox", found_index=0)
                edit = combo_box.child_window(class_name="Edit")
                time.sleep(4)
                if edit.exists():
                    self.logger.debug("Found the editable text control.")
                    edit.set_text(filename)  # Set the filename
                    dialog.type_keys('{ENTER}')  # Press Enter to submit
                    return True
                else:
                    self.logger.debug("Could not find the text box for filename input.")
            except ElementNotFoundError:
                self.logger.debug("Could not find the file dialog window.")

            return False
        return False
    def bring_browser_to_foreground(self):
        if self.os=="win":
            import pygetwindow as gw
            from pywinauto import Application
        try:
            # Find the browser window by title
            window = gw.getWindowsWithTitle(self.driver.title)[0]
            # Bring the window to the foreground
            app = Application().connect(handle=window._hWnd)
            app.top_window().set_focus()
        except IndexError:
            self.logger.debug(f"Window with title '{self.driver.title}' not found.")

    def delete_quit(self, close=True):
        try:
            self.driver.quit()
        except Exception as e:
            self.logger.debug(f"Error quitting driver: {e}")
        if close:
            try:
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], check=True)
                self.logger.debug("All Chrome processes have been terminated.")
            except subprocess.CalledProcessError as e:
                self.logger.debug(f"Error: {e}")

    def open_new_tab(self, open_new=True, close=True):
        if open_new:
            # Open a new tab using JavaScript
            self.driver.execute_script("window.open('');")
            time.sleep(2)
            # Switch to the newly opened tab
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)
        else:
            # Redirect current tab to self.url
            self.driver.get(self.url)
            time.sleep(2)
        if open_new:
            self.driver.get(self.url)
            time.sleep(2)
            # Close the previous tab if needed
            if close:
                self.driver.switch_to.window(self.driver.window_handles[0])
                time.sleep(2)
                self.driver.close()

            # Switch back to the new tab
            self.driver.switch_to.window(self.driver.window_handles[-1])
            time.sleep(2)

    def right_click_middle(self):
        while True:
            # Get the dimensions of the entire web page
            page_width = self.driver.execute_script("return document.documentElement.scrollWidth")
            page_height = self.driver.execute_script("return document.documentElement.scrollHeight")

            # Calculate the middle point
            middle_x = page_width / 2
            middle_y = page_height / 2
            time.sleep(6)
            try:
                # Find the target element (specific div)
                target_element = self.driver.find_element(By.CSS_SELECTOR,
                                                          '.flex.h-full.flex-col.items-center.justify-center.text-token-text-primary .gizmo-shadow-stroke')

                # Move to the middle of the target element and perform a double-click
                actions = ActionChains(self.driver)
                actions.move_to_element(target_element).double_click().perform()
                self.logger.debug("Double-click performed")

                # Ensure the element is focused by clicking it
                target_element.click()
                time.sleep(1)

                # Press the backspace key using pywin32
                win32api.keybd_event(win32con.VK_BACK, 0, 0, 0)
                time.sleep(0.05)  # Sleep for a short duration
                win32api.keybd_event(win32con.VK_BACK, 0, win32con.KEYEVENTF_KEYUP, 0)
                self.logger.debug("Backspace pressed")

                # Check if the file dialog is open
                if self.is_file_dialog_open():

                    break

            except Exception as e:
                self.logger.debug(f"An error occurred: {e}")

            # Small delay before the next iteration
            time.sleep(5)
    def check_redbox_element(self):
        try:
            # Directly targeting the element with a combination of classes and role attribute
            red_box = WebDriverWait(self.driver, 2
).until(
                EC.presence_of_element_located((By.XPATH,
                                                "//div[contains(@class, 'bg-red-500') and contains(@class, 'border-red-500') and @role='alert']"))
            )
            # Check if the specific text is present
            if "Não foi possível carregar" in red_box.text:
                self.logger.debug("The red alert box is present on the page with the specific error message.")
                return True
            else:
                self.logger.debug("The red alert box does not contain the expected error message.")
                return False
        except (NoSuchElementException, TimeoutException):
            self.logger.debug("The red alert box is not found on the page.")
            return False
    def contintue_generating(self):
        selectors = [
        (By.XPATH, "//button[.//div[text()='Continue generating']]"),
        (By.CSS_SELECTOR, "button.btn.relative.btn-secondary.whitespace-nowrap.border-0.md\\:border"),
        (By.CSS_SELECTOR, "button.btn.relative.btn-secondary div svg.icon-xs"),
        (By.CSS_SELECTOR, "button.btn.relative.btn-secondary.whitespace-nowrap.border-0.md\\:border[as='button']"),
        (By.XPATH,
         "//button[contains(@class, 'btn relative btn-secondary') and contains(@class, 'whitespace-nowrap') and @as='button']"),
        (By.XPATH, "//button[.//div[text()='Continue generating']]"), (By.CSS_SELECTOR, "button[as='button']"),
]
        for by, selector in selectors:
            try:
                button = WebDriverWait(self.driver, 2
).until(EC.element_to_be_clickable((by, selector)))
                button.click()
                self.logger.debug(f"Button clicked successfully using {by} with selector: {selector}")
                return True
            except TimeoutException:
                self.logger.debug(f"Button not found or not clickable using {by} with selector: {selector}")

        self.logger.debug("No buttons were found or clickable within the specified timeout.")
        return False


    def check_browser_errs(self):
        selectors = [
            (By.XPATH, "//button[contains(., 'Regenerate')]"),
            (By.XPATH, "//button[@class='btn relative btn-primary m-auto']"),
            (By.XPATH, "//div[@class='flex w-full gap-2 items-center justify-center']//button"),
            (By.CSS_SELECTOR, "button.btn.relative.btn-primary.m-auto"),
            # (By.CSS_SELECTOR, "button[as='button']"),
            # (By.XPATH,"//button[contains(@class, 'btn relative btn-secondary') and contains(@class, 'whitespace-nowrap')]"),


        ]

        for by, selector in selectors:
            try:
                button = WebDriverWait(self.driver, 2
).until(EC.element_to_be_clickable((by, selector)))
                button.click()
                self.logger.debug(f"Button clicked successfully using {by} with selector: {selector}")
                return True
            except TimeoutException:
                self.logger.debug(f"Button not found or not clickable using {by} with selector: {selector}")

        self.logger.debug("No buttons were found or clickable within the specified timeout.")
        return False

    def download_file_with_resume(self,url, filename, retries=5, chunk_size=8192):
        session = requests.Session()
        retry = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # Determine if we already have a partial download
        file_mode = 'ab' if os.path.exists(filename) else 'wb'
        resume_header = {'Range': f'bytes={os.path.getsize(filename)}-'} if file_mode == 'ab' else {}

        with session.get(url, headers=resume_header, stream=True) as response:
            response.raise_for_status()
            with open(filename, file_mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
        return filename

    def __ensure_cf(self, retry: int = 5) -> None:
        '''
        Ensure Cloudflare cookies are set
        :param retry: Number of retries
        '''
        self.logger.debug('Opening new tab...')
        original_window = self.driver.current_window_handle
        self.driver.switch_to.new_window('tab')

        self.logger.debug('Getting Cloudflare challenge...')
        self.driver.get('https://chat.openai.com/api/auth/session')
        try:
            WebDriverWait(self.driver, 3000).until_not(
                EC.presence_of_element_located((By.ID, 'cf_challenge_form'))
            )
        except TimeoutException:
            self.logger.debug(f'Cloudflare challenge failed, retrying {retry}...')
            self.driver.save_screenshot(f'cf_failed_{retry}.png')
            if retry > 0:
                self.logger.debug('Closing tab...')
                self.driver.close()
                self.driver.switch_to.window(original_window)
                return self.__ensure_cf(retry - 1)
            raise ValueError('Cloudflare challenge failed')
        self.logger.debug('Cloudflare challenge passed')

        self.logger.debug('Validating authorization...')
        response = self.driver.page_source
        if response[0] != '{':
            response = self.driver.find_element(By.TAG_NAME, 'pre').text
        response = json.loads(response)
        if (not response) or (
                'error' in response and response['error'] == 'RefreshAccessTokenError'
        ):
            self.logger.debug('Authorization is invalid')
            if not self.__auth_type:
                raise ValueError('Invalid session token')
            self.__login()
        self.logger.debug('Authorization is valid')

        self.logger.debug('Closing tab...')
        self.driver.close()
        self.driver.switch_to.window(original_window)

    def quit_driver(self):
        try:
            self.driver.quit()
        except WebDriverException as e:
            self.logger.error(f"Error quitting driver: {e}")
        finally:
            self.kill_chrome_processes()

    def kill_chrome_processes(self):
        import subprocess

        try:
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], check=True)
            self.logger.debug("All Chrome processes have been terminated.")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error: {e}")

    def __login(self) -> None:
        '''
        Login to ChatGPT
        '''
        self.logger.debug('Opening new tab...')
        original_window = self.driver.current_window_handle
        self.driver.switch_to.new_window('tab')

        self.logger.debug('Opening login page...')
        self.driver.get('https://chat.openai.com/auth/login')

        self.logger.debug('Clicking login button...')
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(chatgpt_login_btn)
        ).click()

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(chatgpt_login_h1)
        )


        self.logger.debug('Checking if login was successful')
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(chatgpt_logged_h1)
            )
            if self.__login_cookies_path:
                self.logger.debug('Saving cookies...')
                with open(self.__login_cookies_path, 'w', encoding='utf-8') as f:
                    json.dump(
                        [
                            i
                            for i in self.driver.get_cookies()
                            if i['name'] == '__Secure-next-auth.session-token'
                        ],
                        f,
                    )
        except SeleniumExceptions.TimeoutException as e:
            self.driver.save_screenshot('login_failed.png')
            raise e

        self.logger.debug('Closing tab...')
        self.driver.close()
        self.driver.switch_to.window(original_window)

    def __keep_alive(self) -> None:
        '''
        Keep the session alive by updating the local storage\n
        Credit to Rawa#8132 in the ChatGPT Hacking Discord server
        '''
        while self.__is_active:
            self.logger.debug('Updating session...')
            payload = (
                    '{"event":"session","data":{"trigger":"getSession"},"timestamp":%d}'
                    % int(time.time())
            )
            try:
                self.driver.execute_script(
                    'window.localStorage.setItem("nextauth.message", arguments[0])',
                    payload,
                )
            except Exception as e:
                self.logger.debug(f'Failed to update session: {str(e)}')
            time.sleep(60)

    def __check_blocking_elements(self) -> None:
        '''
        Check for blocking elements and dismiss them
        '''
        self.logger.debug('Looking for blocking elements...')
        try:
            intro = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(chatgpt_intro)
            )
            self.logger.debug('Dismissing intro...')
            self.driver.execute_script('arguments[0].remove()', intro)
        except SeleniumExceptions.TimeoutException:
            pass

        alerts = self.driver.find_elements(*chatgpt_alert)
        if alerts:
            self.logger.debug('Dismissing alert...')
            self.driver.execute_script('arguments[0].remove()', alerts[0])

    def delete_quit(self,close=True):
        self.logger.debug('deleting the chat and quiting the browser')
        self.logger.debug("deleting the chat")
        if self.os=="win":
            pyautogui_args =["ctrl","shift","delete"]
        if self.os=="mac":
            pyautogui_args =["command","shift","delete"]
        pyautogui.hotkey(*pyautogui_args)
        pyautogui.press("return")
        time.sleep(2)
        if close:
            self.driver.close()
        if not close:
            self.driver.quit()

    def click_file_Menubar(self):
        div_xpath_list = [
            "//div[@role='menuitem' and contains(@class, 'flex items-center') and contains(@class, 'cursor-pointer') and .//text()='Carregar do computador']",
            "//div[@role='menuitem' and .//text()='Carregar do computador']",
            "//div[@role='menuitem' and contains(@class, 'cursor-pointer') and contains(text(), 'Carregar do computador')]",
            "//div[@role='menuitem' and contains(text(), 'Carregar do computador')]",
            "//div[contains(@class, 'radix-state-open:bg-[#f5f5f5]') and .//text()='Carregar do computador']",
            "//*[@id='radix-:rj:']//div[contains(text(), 'Carregar do computador')]",
            "//*[@id='radix-:rj:']/div[contains(@class, 'flex items-center') and contains(text(), 'Carregar do computador')]",
            "#radix-\\:rj\\: > div:nth-child(5)",
            "//div[@role='menuitem' and @tabindex='-1' and contains(@class, 'radix-state-open:bg-[#f5f5f5]') and .//text()='Carregar do computador']",
            "//div[@role='menuitem' and contains(@class, 'dark:hover:bg-token-main-surface-secondary') and .//text()='Carregar do computador']",
            "//div[@role='menuitem' and @data-orientation='vertical' and .//text()='Carregar do computador']",
            "//div[@role='menuitem' and @data-radix-collection-item and .//text()='Carregar do computador']",
            "//div[@role='menuitem' and @tabindex='-1' and contains(@class, 'dark:hover:bg-token-main-surface-secondary') and .//text()='Carregar do computador']",
            "//div[@role='menuitem' and contains(@class, 'm-1.5 p-2.5 text-sm cursor-pointer focus-visible:outline-0 radix-disabled:pointer-events-none radix-disabled:opacity-50 group relative hover:bg-[#f5f5f5] focus-visible:bg-[#f5f5f5] dark:hover:bg-token-main-surface-secondary dark:focus-visible:bg-token-main-surface-secondary rounded-md my-0 px-3 mx-2 radix-state-open:bg-[#f5f5f5] dark:radix-state-open:bg-token-main-surface-secondary gap-2.5 py-3') and .//text()='Carregar do computador']",
            # New XPath targeting the full class chain and visible text
            "#radix-\\:rk\\: > div:nth-child(5)",  # Corrected CSS selector
            "//*[@id='radix-:rk:']/div[5]"  # New XPath for direct child positioning
        ]

        for div_selector in div_xpath_list:
            try:
                # Determine if the selector is an XPath or CSS Selector
                if div_selector.startswith('//') or div_selector.startswith('('):
                    div_element = WebDriverWait(self.driver, 2
).until(
                        EC.visibility_of_element_located((By.XPATH, div_selector))
                    )
                    # Ensure the element is clickable before clicking it
                    WebDriverWait(self.driver, 2
).until(
                        EC.element_to_be_clickable((By.XPATH, div_selector))
                    )
                else:
                    div_element = WebDriverWait(self.driver, 2
).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, div_selector))
                    )
                    # Ensure the element is clickable before clicking it
                    WebDriverWait(self.driver, 2
).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, div_selector))
                    )

                # Scroll the element into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", div_element)

                try:
                    div_element.click()
                except Exception as e:
                    self.logger.debug(f"Selenium click failed, using JavaScript click: {e}")
                    self.driver.execute_script("arguments[0].click();", div_element)

                self.logger.debug(f"Clicked on the specified <div> element with selector: {div_selector}")
                return True  # Exit if an element is clicked successfully

            except Exception as e:
                self.logger.debug(f"Specified <div> element with selector {div_selector} not clickable. Error: {e}")

        raise Exception("File dialogue button not found. Please update the div xpath list.")

    def click_files_button(self):
        xpath_list = [
            # Precise XPath for the main div containing the button
            "//*[@id='__next']/div[1]/div[2]/main/div[1]/div[2]/div[1]/div/form/div/div[2]/div/div/div[1]/div",

            # XPath for the button with specific ID within the flex flex-col div
            "//div[contains(@class, 'flex flex-col')]//button[@id='radix-:ra:' and @aria-haspopup='menu']",

            # XPath for the button with specific class attributes within the flex flex-col div
            "//div[contains(@class, 'flex flex-col')]//button[contains(@class, 'flex items-center justify-center h-8 w-8 rounded-full text-token-text-primary focus-visible:outline-black dark:text-white dark:focus-visible:outline-white mb-1 ml-1.5') and @aria-disabled='false']",

            # XPath for the div with specific attributes within the flex flex-col div
            "//div[contains(@class, 'flex flex-col')]//div[@type='button' and @aria-haspopup='dialog' and @data-state='closed']",

            # Additional XPath for the SVG path within the button
            "//div[contains(@class, 'flex flex-col')]//button[contains(@class, 'flex items-center justify-center h-8 w-8 rounded-full text-token-text-primary focus-visible:outline-black dark:text-white dark:focus-visible:outline-white mb-1 ml-1.5') and @aria-disabled='false']/svg/path[@fill='currentColor' and @fill-rule='evenodd']",

            # XPath for any button within the specified main div path
            "//*[@id='__next']/div[1]/div[2]/main/div[1]/div[2]/div[1]/div/form/div/div[2]/div/div/div[1]/div/button",

            # XPath for any element with aria-haspopup attribute set to menu
            "//*[@aria-haspopup='menu']"
        ]

        for selector in xpath_list:
            try:
                # Determine if the selector is an XPath or CSS Selector
                if selector.startswith('//') or selector.startswith('('):
                    elements = self.driver.find_elements(By.XPATH, selector)
                    locator = (By.XPATH, selector)
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    locator = (By.CSS_SELECTOR, selector)

                if not elements:
                    self.logger.debug(f"No elements found for selector: {selector}")
                    continue

                # Wait until the element is clickable
                button = WebDriverWait(self.driver, 2
).until(
                    EC.element_to_be_clickable(locator)
                )
                button.click()
                self.logger.debug(f"Clicked button with selector: {selector}")
                return True  # Exit after clicking the first clickable button
            except Exception as e:
                self.logger.debug(f"Button with selector {selector} not clickable. Error: {e}")

        raise Exception("File dialogue button not found. Please update the div xpath list.")
        time.sleep(4)


    def insert_pdfs(self,path):
        self.logger.debug('start insert pdfs function' )
        self.logger.debug("Waiting for the button to be clickable...")
        # self.right_click_middle()
        self.click_files_button()
        time.sleep(2)
        self.click_file_Menubar()
        time.sleep(3)
        dialogue = self.is_file_dialog_open(path)
        if dialogue==True:

            if self.check_redbox_element()==True:
                self.logger.debug('no redbox element' * 20)
                self.logger.debug('__' * 20)
                return False
            else:
                self.sleep(20)
    
                # Wait for the file to be uploaded (adjust time as necessary)
                self.logger.debug("Waiting for the file to upload...")
                self.logger.debug('__' * 20)
                return True
        else:
            self.logger.debug("Not dialogue")
            self.logger.debug(dialogue)
            
            
        # elif self.click_files_button():
        #     # Wait for the file dialog to open
        #     self.logger.debug("Waiting for the file dialog to open...")
        #     time.sleep(2)  # Adjust this delay to ensure the file dialog is open

            # Copy the 'path' value to the clipboard

            # pyperclip.copy(path)  # Copy path to clipboard
            # self.logger.debug("File copied to clipboard.")
            # if self.os == "mac":
            #     pyautogui.hotkey('command', 'shift','g')  # Paste the path from the clipboard
            #     time.sleep(5)  # Wait a moment for the paste action to complete
            #     self.logger.debug("Pasting the path in the file dialog...")
            #     pyautogui.hotkey('command', 'v')  # Paste the path from the clipboard
            #     time.sleep(2)  # Wait a moment for the paste action to complete
            #     pyautogui.press('enter')  # Press enter to submit the dialog
            #     time.sleep(2)
            #     pyautogui.press('enter')  # Press enter to submit the dialog
            #     self.logger.debug("submit.")
            # if self.os == "win":
            #     if self.is_file_dialog_open(path):
            #         time.sleep(2)
            #
            #
            #     else:
            #         raise Exception("File dialogue button not found.Please update the xpath list")
            #     time.sleep(5)
                    # The following key actions are intended for the file dialog,
                # self.logger.debug("Pasting the path in the file dialog...")
                # pyautogui.hotkey('ctrl', 'v')  # Paste the path from the clipboard
                # self.logger.debug("Pasted the path.")
                # time.sleep(3)  # Wait a moment for the paste action to complete
                # pyautogui.press('enter')  # Press enter to submit the dialog
                # self.logger.debug("Pressed return.")
            # if self.check_redbox_element():
            #     return False
            # else:
            #     return True




    def interact_with_page(self, path, prompt="",copy=True):
        self.logger.debug('Start interacting with page function...')

        pyautogui.press('esc', 2)
        self.logger.debug('esc clicked twice...')

        continue_func=False
        while not continue_func:
            if type(path)==str:
                self.logger.debug('one path found...')

                continue_func=self.insert_pdfs(path)
                if continue_func==False:
                    self.interact_with_page(path=path, prompt=prompt, copy=copy)
            if type(path) == list:
                self.logger.debug(f'{len(path)} paths found...')

                for pdf_path in path:
                    continue_func=self.insert_pdfs(pdf_path)
                if continue_func==False:
                    self.interact_with_page(path=path, prompt=prompt, copy=copy)
        if copy :
            content =self.send_message(message=prompt)
            self.logger.debug('interacting with page function copy mode on' * 20)

            self.logger.debug('__' * 20)

            return content
            # if continue_func==True:
            #     break
            time.sleep(5)
        self.logger.debug('interacting with page function copy mode off...')
        self.logger.debug('__'*20)

    def sleep(self,sleep_duration):

        config_handler.set_global(spinner='dots_waves2', bar='bubbles', theme='smooth')

        # Determine the maximum width for the progress bar to ensure it fits in the display area
        max_bar_width = 30  # You can adjust this value based on your terminal size or preferences

        # Initialize the alive_progress bar with enhanced style, force_tty=True, and a constrained width
        with alive_bar(sleep_duration, force_tty=True, title="Sleeping...", bar="blocks", spinner="dots_waves2",
                       length=max_bar_width) as bar:
            for i in range(sleep_duration):
                time.sleep(1)  # Sleep for a second
                bar()  # Update the progress bar by one unit
                # Dynamic message showing remaining time in minutes, using 'i' to track progress
                # remaining_time = (sleep_duration - (i + 1)) / 60  # '+ 1' because 'i' starts from 0
                # bar.text(f'Remaining: {remaining_time:.2f} min')

    def copy_message(self):
        self.logger.debug('Start copy message function...')

        # Copy the response by the shortcut Ctrl+Shift+;
        try:
            # Wait until the button appears, with a timeout of 10 seconds
            button = WebDriverWait(self.driver, 2
).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "btn-primary"))
            )
            # Click the button if it is visible
            button.click()
        except Exception as e:
            pass
            # If the button does not appear, pass
            # self.logger.debug("Button not found, passing. Error: ", e)

        textbox = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(chatgpt_textbox)
        )
        for i in range(3):
            pyautogui.press('esc', 2)
            time.sleep(2)
            self.logger.debug("esc")
       
        textbox.click()
        if self.os == "win":
            pyautogui_arg = ['ctrl', 'shift', ';']
        if self.os == "mac":
            pyautogui_arg = ['command', 'shift', ';']

        pyautogui.FAILSAFE = False
        time.sleep(5)
        #
        # pyautogui.click()
        # Press Control, Shift, and ;
        pyautogui.hotkey(*pyautogui_arg)
        content = pyperclip.paste()
        self.logger.debug('code copied...')
        self.logger.debug('__'*20)

        return content

    def send_message(self, message: str,sleep_duration:int=5) -> dict:
        '''
        Send a message to ChatGPT\n
        :param message: Message to send
        :return: Dictionary with keys `message` and `conversation_id`
        '''
        self.logger.debug('Start send message function' * 20)
        self.logger.debug('Ensuring Cloudflare cookies...')
        self.__ensure_cf()
        self.logger.debug('Sending message...')
        textbox = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(chatgpt_textbox)
        )
        # Copy the message to the clipboard
        pyperclip.copy(message)
        # Create an ActionChain to perform a paste operation
        textbox.click()
        actions = ActionChains(self.driver)
        if self.os == "win":
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        if self.os == "mac":
            actions.key_down(Keys.COMMAND).send_keys('v').key_up(Keys.CONTROL).perform()

        textbox.send_keys(Keys.ENTER)
        self.logger.debug('Waiting for completion...')
        self.logger.debug("message sent and now waiting {} for getting response".format(sleep_duration))


        self.sleep(sleep_duration)
        if self.check_browser_errs():
            self.logger.debug('regenerate button found and clicked: resending message.')

            self.send_message(message)
        if self.contintue_generating():
            time.sleep(30)
        self.logger.debug('__' * 20)
        return self.copy_message()



