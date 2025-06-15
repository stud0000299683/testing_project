import urllib

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from payment_class import PaymentPage
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import subprocess
import os
import time


@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope="module", autouse=True)
def server_start():
     process = subprocess.Popen(
        [python_path, "-m", "http.server", "8000"],
        cwd=os.path.join(os.path.dirname(__file__), "..", "dist"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    #process = subprocess.Popen(["C://Users//chamorcev//AppData//Local//Programs//Python//Python312//python.exe", "-m", "http.server", "8000"],
    #                           cwd=os.path.join(os.path.dirname(__file__), "..", "dist"),
    #                           stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE)
    for _ in range(10):
        try:
            urllib.request.urlopen("http://localhost:8000")
            break
        except:
            time.sleep(0.5)
    else:
        pytest.fail("Server did not start in time")

    yield
    process.terminate()
    process.wait()


# Проверяем что сервис доступен и страница открывается
def test_open_page(driver):
    page = PaymentPage(driver)
    page.open()
    assert "F-Bank" in driver.title


# Проверяем отправку при пустом значении суммы к переводу
def test_clear_amount(driver):
    page = PaymentPage(driver)
    page.open()
    page.select_ruble_account()
    page.enter_card_number("1111 2222 3333 4444")
    page.clear_amount()
    try:
        WebDriverWait(driver, 5).until(
            lambda _: page.is_transfer_button_disabled() or not page.is_transfer_button_visible()
        )
    except TimeoutException:
        pass
    assert page.is_transfer_button_disabled() or not page.is_transfer_button_visible(), \
        "Кнопка 'Перевести' должна быть заблокирована или скрыта без суммы"


# Проверяем возможность ввести 17 цифр карты
def test_invalid_card_number_17_digits(driver):
    page = PaymentPage(driver)
    page.open()
    page.select_ruble_account()
    page.enter_card_number("1111 2222 3333 4444 5")
    error = page.get_error_message()
    assert error == "Номер карты должен содержать 16 цифр", "Ожидалась ошибка валидации"


# Проверяем возможность ввести 15 цифр карты
def test_invalid_card_number_15_digits(driver):
    page = PaymentPage(driver)
    page.open()
    page.select_ruble_account()
    page.enter_card_number("1111 2222 3333 444")
    assert page.is_amount_disabled, "При неполном номере карты поле ввода суммы должно быть скрыто"


# Проверяем возможность отправить минусовую сумму
def test_negative_amount(driver):
    page = PaymentPage(driver)
    page.open()
    page.select_ruble_account()
    page.enter_card_number("1111 2222 3333 4444")
    page.enter_amount("-1000")
    error = page.get_error_message()
    assert error == "Сумма не может быть отрицательной", "Ожидалась ошибка при отрицательной сумме"


# Проверяем возможность осуществить перевод с копейками
def test_decimal_amount(driver):
    page = PaymentPage(driver)
    page.open()
    page.select_ruble_account()
    page.enter_card_number("1111 2222 3333 4444")
    page.enter_amount("1000.50")
    page.get_amount()
    assert page.get_amount() == "1000.50",  "Дробные суммы должны быть допустимы"


# Проверяем перевод суммы в 1000 рублей
def test_successful_transfer_alert(driver):
    page = PaymentPage(driver)
    page.open()
    page.select_ruble_account()
    page.enter_card_number("1111 2222 3333 4444")
    page.enter_amount("1000")
    page.click_transfer_button()
    alert_text = page.get_alert_text()
    assert alert_text.startswith("Перевод 1000"), "Неверная сумма в алерте"


# Тесты которые еще можно добавить

# Проверяем комиссию
def test_comission(driver):
    pass


def test_max_amount(driver):
    pass


def test_amount_more_than_account(driver):
    pass
