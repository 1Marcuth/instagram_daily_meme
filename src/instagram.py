from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pydantic import validate_call
from selenium import webdriver
from logging import warning
import pyperclip
import time
import os

from utils.file import write_json_file, read_json_file
from utils.url import extract_domain

class Instagram:
    BASE_URL = "https://www.instagram.com"

    @validate_call
    def __init__(self, user_data_path: str) -> None:
        manager = ChromeDriverManager()
        service = webdriver.ChromeService(executable_path = manager.install())
        options = webdriver.ChromeOptions()

        options.add_argument("--start-maximized")

        self._driver = webdriver.Chrome(options = options, service = service)

        self._driver.get("https://google.com/")

    def _save_cookies(self) -> None:
        current_domain = extract_domain(self._driver.current_url)
        file_path = f".user_data/{current_domain}.json"
        cookies = self._driver.get_cookies()
        write_json_file(file_path, cookies)

    def _load_cookies(self) -> None:
        current_domain = extract_domain(self._driver.current_url)
        file_path = f".user_data/{current_domain}.json"

        if os.path.exists(file_path):
            cookies = read_json_file(file_path)
            
            for cookie in cookies:
                self._driver.add_cookie(cookie)
            
            self._driver.refresh()

    def _close_notifications_popup(self) -> None:
        try:
            self._driver.implicitly_wait(5)
            notifications_element = self._driver.find_element(By.XPATH, "//*[contains(text(), 'Agora não')]")
            notifications_element.click()
            self._save_cookies()
        except:
            warning("Unable to find Notification Popup, possibly already closed.")

    def _create_content(self) -> None:
        self._driver.implicitly_wait(10)
        create_content_button = self._driver.find_element(By.XPATH, "//*[contains(text(), 'Criar')]")
        create_content_button.click()

    @validate_call
    def _select_files(self, file_paths: list[str]) -> None:
        file_paths_string = "\n".join(file_paths)

        self._driver.implicitly_wait(5)
        file_input_element = self._driver.find_element(By.CSS_SELECTOR, "input[type='file'][multiple]")

        self._driver.execute_script("arguments[0].style.display = 'block';", file_input_element)
        file_input_element.send_keys(file_paths_string)

        self._save_cookies()

    def _close_reel_notice(self) -> None:
        try:
            self._driver.implicitly_wait(10)
            reel_element = self._driver.find_element(By.XPATH, "//*[text()='OK']")
            reel_element.click()
            self._save_cookies()
        
        except:
            warning("Unable to find Reel Popup, possibly already closed.")

    @validate_call
    def _put_caption(self, caption: str) -> None:
        self._driver.implicitly_wait(5)

        caption_element = self._driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
        caption_element.click()

        pyperclip.copy(caption)
        action = webdriver.ActionChains(self._driver)

        (action
            .key_down(Keys.CONTROL)
            .send_keys("v")
            .key_up(Keys.CONTROL)
            .perform())

    def _next(self) -> None:
        self._driver.implicitly_wait(5)
        next_element = self._driver.find_element(By.XPATH, "//*[contains(text(), 'Avançar')]")
        next_element.click()

    def _share(self) -> None:
        self._driver.implicitly_wait(15)
        next_element = self._driver.find_element(By.XPATH, "//*[contains(text(), 'Compartilhar')]")
        next_element.click()

    @validate_call
    def create_post(
        self,
        media_file_paths: list[str],
        caption: str,
        location: str
    ) -> None:
        self._create_content()
        self._select_files(media_file_paths)
        self._close_reel_notice()
        self._next()
        self._next()
        self._put_caption(caption)
        self._share()
        self._save_cookies()


    @validate_call
    def login(
        self,
        username: str,
        password: str
    ) -> None:
        self._driver.get(self.BASE_URL)
        self._load_cookies()
        time.sleep(3)

        try:
            username_input = WebDriverWait(self._driver, 10).until(
                EC.element_to_be_selected((By.CSS_SELECTOR, "input[name=\"username\"]"))
            )
             
            password_input = self._driver.find_element(By.CSS_SELECTOR, "input[name=\"password\"]")
            enter_button = self._driver.find_element(By.CSS_SELECTOR, "button[type=\"submit\"]")

            actions = [ lambda: username_input.send_keys(username), lambda: password_input.send_keys(password), lambda: enter_button.click() ]

            for action in actions:
                action()
                time.sleep(2)

        except:
            warning("An error occurred when trying to log in to the user's account, possibly the user is already logged in.")

        self._save_cookies()
        self._close_notifications_popup()