import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pygetwindow as gw
from pywinauto import Application
import time

# Function to bring the browser to the foreground
def bring_browser_to_foreground(window_title):
    try:
        # Find the browser window by title
        window = gw.getWindowsWithTitle(window_title)[0]
        # Bring the window to the foreground
        app = Application().connect(handle=window._hWnd)
        app.top_window().set_focus()
    except IndexError:
        print(f"Window with title '{window_title}' not found.")

# Function to minimize the browser
def minimize_browser(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.minimize()
    except IndexError:
        print(f"Window with title '{window_title}' not found.")

# Function to maximize the browser
def maximize_browser(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        window.maximize()
    except IndexError:
        print(f"Window with title '{window_title}' not found.")

# Define Chrome options
options = uc.ChromeOptions()
options.add_argument("--user-data-dir=C:\\Users\\luano\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("--profile-directory=Profile 2")
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

# Initialize the WebDriver with the options
driver = uc.Chrome(options=options)

# Open the desired webpage
url = 'https://chat.openai.com'
print(f"Navigating to {url}")
driver.get(url)

# Wait a bit for the page to load
time.sleep(5)
print(f"Current URL: {driver.current_url}")
if driver.current_url == url:
    print("Successfully navigated to the URL")
else:
    print("Failed to navigate to the URL")

# Get the browser window title
window_title = driver.title
print(f"Window title: {window_title}")

# Wait 5 seconds and then minimize the browser
time.sleep(5)
minimize_browser(window_title)
print("Browser minimized")

# Wait another 5 seconds and then maximize the browser
time.sleep(5)
maximize_browser(window_title)
print("Browser maximized")

# Optionally, bring the browser to the foreground at will
bring_browser_to_foreground(window_title)
print("Browser brought to foreground")

# Add a final delay before quitting to observe the browser state
time.sleep(10)
driver.quit()
