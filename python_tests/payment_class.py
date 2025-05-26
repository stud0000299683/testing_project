import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pytest


class PaymentPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "http://localhost:8000/?balance=30000&reserved=20000"
        self.sum_input_element = "/html/body/div/div/div/div[2]/input[2]"
        self.transfer_button_element = "/html/body/div/div/div/div[2]/button/span"
        self.ruble_button_element = "/html/body/div/div/div/div[1]/div[1]"
        self.card_number_element = "/html/body/div/div/div/div[2]/input[1]"
        self.error_message_element = "/html/body/div/div/div/div[2]/span[2]"

    def open(self):
        self.driver.get(self.url)
        print("Opened page:", self.driver.title)

    def select_ruble_account(self):
        button = self.driver.find_element(By.XPATH, self.ruble_button_element)
        button.click()

    def enter_card_number(self, card_number):
        card_input = self.driver.find_element(By.XPATH, self.card_number_element)
        card_input.clear()
        card_input.send_keys(card_number)

    def enter_amount(self, amount):
        sum_input = self.driver.find_element(By.XPATH, self.sum_input_element)
        sum_input.clear()
        sum_input.send_keys(amount)

    def get_amount(self):
        sum_input = self.driver.find_element(By.XPATH, self.sum_input_element)
        return sum_input.get_attribute("value")

    def clear_amount(self):
        sum_input = self.driver.find_element(By.XPATH, self.sum_input_element)
        sum_input.clear()
        sum_input.send_keys()

    def click_transfer_button(self):
        button = self.driver.find_element(By.XPATH, self.transfer_button_element)
        button.click()

    def get_error_message(self):
        try:
            error = self.driver.find_element(By.XPATH, self.error_message_element)
            time.sleep(10)
            return error.text
        except:
            return None

    def is_amount_disabled(self):
        amount = self.driver.find_element(By.XPATH, self.sum_input_element)
        return not amount.is_enabled()

    def is_transfer_button_disabled(self):
        button = self.driver.find_element(By.XPATH, self.transfer_button_element)
        return not button.is_enabled()

    def accept_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            return True
        except:
            return False

    def is_transfer_button_visible(self):
        try:
            button = self.driver.find_element(By.XPATH, self.transfer_button_element)
            return button.is_displayed()
        except:
            return False

    def get_alert_text(self):
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text
            alert.accept()
            return text
        except TimeoutException:
            pytest.fail("Alert не появился в течение 5 секунд")

    def verify_alert_content(self, amount, currency, card_number):
        alert_text = self.get_alert_text()
        expected_pattern = f"Перевод {amount} {currency} на карту {card_number} принят банком!"
        assert alert_text == expected_pattern, \
            f"Alert текст не совпадает. Ожидалось: {expected_pattern}, получено: {alert_text}"
