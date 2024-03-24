from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions as SeleniumExceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pyautogui

pyautogui.FAILSAFE = False

timeout = 300
from tqdm import tqdm
from tqdm.auto import tqdm as auto_tqdm

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
from selenium.common.exceptions import TimeoutException
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
    '''
    An unofficial Python wrapper for OpenAI's ChatGPT API
    '''

    def __init__(
            self,
            session_token: str = None,
            conversation_id: str = '',
            chat_id: str = None,
            auth_type: str = None,
            email: str = None,
            password: str = None,
            login_cookies_path: str = '',
            captcha_solver: str = 'pypasser',
            solver_apikey: str = '',
            proxy: str = None,
            chrome_args: list = [],
            moderation: bool = True,
            verbose: bool = False,
            check_url: bool = True
    ):
        '''
        Initialize the ChatGPT object\n
        :param session_token: The session token to use for authentication
        :param conversation_id: The conversation ID to use for the chat session
        :param auth_type: The authentication type to use (`google`, `microsoft`, `openai`)
        :param email: The email to use for authentication
        :param password: The password to use for authentication
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
        self.__email = email
        self.__password = password
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

        if not self.__session_token and (
                not self.__email or not self.__password or not self.__auth_type
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

    def __init_logger(self, verbose: bool) -> None:
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

    def __init_browser(self) -> None:
        '''
        Initialize the browser
        '''

        self.logger.debug('Initializing browser...')

        options = uc.ChromeOptions()
        options.add_argument('--window-size=1024,568')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if self.__proxy:
            options.add_argument(f'--proxy-server={self.__proxy}')
        for arg in self.__chrome_args:
            options.add_argument(arg)
        try:
            webdriver_path = ChromeDriverManager().install()
            self.driver = uc.Chrome(driver_executable_path=webdriver_path, options=options)

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
                self.chat_id = "bo0FiWLY7-consensus"
            if self.chat_id == "scholar":
                self.chat_id = "kZ0eYXlJe-scholar-gpt"
            if self.chat_id == "scispace":
                self.chat_id = "NgAcklHd8-scispace"
            if self.chat_id == "askpdf":
                self.chat_id = "UfFxTDMxq-askyourpdf-research-assistant"
            if self.chat_id == "lit":
                self.chat_id = "lfY2IC1TZ-auto-literature-review"

            if self.chat_id == "pdf":
                self.chat_id = "l3aJUSU8K-ask-pdf"
            self.url = f'https://chat.openai.com//g/g-{self.chat_id}'
            self.driver.get(self.url)
            if self.chat_id == "":
                self.driver.get(f'https://chat.openai.com')
        else:
            self.driver.get(f'{chatgpt_chat_url}/{self.__conversation_id}')
        self.__check_blocking_elements()

        self.__is_active = True
        Thread(target=self.__keep_alive, daemon=True).start()

    def __ensure_cf(self, retry: int = 3) -> None:
        '''
        Ensure Cloudflare cookies are set\n
        :param retry: Number of retries
        '''
        self.logger.debug('Opening new tab...')
        original_window = self.driver.current_window_handle
        self.driver.switch_to.new_window('tab')

        self.logger.debug('Getting Cloudflare challenge...')
        self.driver.get('https://chat.openai.com/api/auth/session')
        try:
            WebDriverWait(self.driver, 3000).until_not(
                EC.presence_of_element_located(cf_challenge_form)
            )
        except SeleniumExceptions.TimeoutException:
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

    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    def interact_with_page(self, path, prompt="", copy=False):

        self.logger.debug('Ensuring Cloudflare cookies...')
        self.__ensure_cf()
        enabled_button = None

        # Press Esc to close the 'Find' box
        pyautogui.press('esc', 2)

        # Press ESCAPE to close the search box
        """
        This function takes a dictionary with 'path' and 'prompt' as keys.
        It will find a button, click it, wait, copy the 'path' value to the clipboard, paste it,
        press the return key, wait, and print the 'prompt'.
        """
        print("Starting interaction with the page...")

        # Click the button by its class name
        try:
            print("Waiting for the button to be clickable...")
            button_xpath = "//button[contains(@class,'btn')][contains(@class,'relative')][contains(@class,'p-0')][@aria-label='Attach files']"
            button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            button.click()
            print("Clicked the button.")

            # Wait for the file dialog to open
            print("Waiting for the file dialog to open...")
            time.sleep(2)  # Adjust this delay to ensure the file dialog is open

            # Copy the 'path' value to the clipboard

            pyperclip.copy(path)  # Copy path to clipboard

            # The following key actions are intended for the file dialog,
            print("Pasting the path in the file dialog...")
            time.sleep(1)  # Wait a moment for the dialog to fully gain focus
            pyautogui.hotkey('ctrl', 'v')  # Paste the path from the clipboard
            print("Pasted the path.")
            time.sleep(3)  # Wait a moment for the paste action to complete
            pyautogui.press('enter')  # Press enter to submit the dialog
            print("Pressed return.")

            # Wait for the file to be uploaded (adjust time as necessary)
            print("Waiting for the file to upload...")

            time.sleep(60 * 2)

            if copy:
                self.logger.debug('Sending message...')
                textbox = WebDriverWait(self.driver, 3600).until(
                    EC.element_to_be_clickable(chatgpt_textbox)
                )
                pyperclip.copy(prompt)

                # Create an ActionChain to perform a paste operation
                textbox.click()
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

                textbox.send_keys(Keys.ENTER)
                time.sleep(30)
                print('Copying text')

                try:
                    send_button = WebDriverWait(self.driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='send-button']"))
                    )
                    send_button.click()
                    print("Button clicked successfully.")

                except Exception as e:
                    pyautogui.press('enter')  # Press enter to submit the dialog

                    print(f"An error occurred with send button: {e}")

                sleep_duration = 60 * 1
                self.sleep(sleep_duration)

                textbox.click()
                actions2 = ActionChains(self.driver)
                actions2.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys(';').key_up(Keys.CONTROL).key_up(
                    Keys.SHIFT).perform()
                time.sleep(5)
                pyautogui.click()
                # Press Control, Shift, and ;
                pyautogui.hotkey('ctrl', 'shift', ';')
                content = pyperclip.paste()
                print("copied")
                time.sleep(6)
                return content


        except Exception as e:
            print(f"An error occurred with interact function: {e}")

    def open_new_tab(self):
        # Open a new tab
        self.driver.execute_script("window.open()")

        # Switch to the newly opened tab
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Navigate to the URL
        self.driver.get(self.url)



    def sleep(self, sleep_duration):
        with tqdm(total=sleep_duration, desc="Sleeping", bar_format="{l_bar}{bar:30}{r_bar}{bar:-30b}",
                  colour='yellow') as pbar:
            start_time = time.time()
            while time.time() - start_time < sleep_duration:
                time.sleep(1)
                remaining_time = int(sleep_duration - (time.time() - start_time))
                pbar.set_postfix({"Remaining": remaining_time})
                pbar.update(0)  # Update the progress bar without incrementing
            pbar.update(sleep_duration)  # Ensure the progress bar is complete at the end

    def send_message(self, message: str, copy=True) -> dict:
        '''
        Send a message to ChatGPT\n
        :param message: Message to send
        :return: Dictionary with keys `message` and `conversation_id`
        '''

        response = None  # or "" if an empty string makes more sense in your context
        #
        # self.logger.debug('Ensuring Cloudflare cookies...')
        # self.__ensure_cf()

        # self.logger.debug('Sending message...')
        textbox = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(chatgpt_textbox)
        )

        # Copy the message to the clipboard
        # Either copy and paste the message or type it directly
        pyperclip.copy(message)

        # Create an ActionChain to perform a paste operation
        textbox.click()
        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        textbox.send_keys(Keys.ENTER)
        self.logger.debug('Waiting for completion...')

        self.logger.debug('Getting response...')

        sleep_duration = 60 * 4  # 4 minutes
        self.sleep(sleep_duration)
        # Copy the response by the shortcut Ctrl+Shift+;
        try:
            if copy:
                textbox = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(chatgpt_textbox)
                )
                print('Copying code')
                textbox.click()
                actions2 = ActionChains(self.driver)
                actions2.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys(';').key_up(Keys.CONTROL).key_up(
                    Keys.SHIFT).perform()
                pyautogui.FAILSAFE = False
                time.sleep(5)

                pyautogui.click()
                # Press Control, Shift, and ;
                pyautogui.hotkey('ctrl', 'shift', ';')
                content = pyperclip.paste()
                print("copied")

            else:
                textbox = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(chatgpt_textbox)

                )
                print('Copying text')

                textbox.click()
                actions2 = ActionChains(self.driver)
                actions2.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys('c').key_up(Keys.CONTROL).key_up(
                    Keys.SHIFT).perform()
                time.sleep(5)
                pyautogui.click()
                # Press Control, Shift, and ;
                pyautogui.hotkey('ctrl', 'shift', 'c')
                content = pyperclip.paste()
                print("copied")

            return content
        except SeleniumExceptions.TimeoutException as e:

            self.driver.save_screenshot('copy error.png')
            raise e


