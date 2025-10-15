import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver.firefox.options import Options as FFOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from decimal import Decimal


URL = "https://www.saucedemo.com/"
USER = "standard_user"
PWD = "secret_sauce"


@pytest.fixture
def driver():
    opts = FFOptions()
    service = FFService(GeckoDriverManager().install())
    drv = webdriver.Firefox(service=service, options=opts)
    drv.maximize_window()
    yield drv
    drv.quit()


def test_checkout_total(driver):
    wait = WebDriverWait(driver, 15)
    driver.get(URL)

    # логин
    wait.until(EC.visibility_of_element_located((By.ID, "user-name"))).send_keys(USER)
    driver.find_element(By.ID, "password").send_keys(PWD)
    driver.find_element(By.ID, "login-button").click()

    # добавляем 3 товара (по data-test у кнопок)
    def add(data_test: str):
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"[data-test='{data_test}']"))
        ).click()

    add("add-to-cart-sauce-labs-backpack")
    add("add-to-cart-sauce-labs-bolt-t-shirt")
    add("add-to-cart-sauce-labs-onesie")

    # корзина
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "shopping_cart_link"))).click()

    # checkout
    wait.until(EC.element_to_be_clickable((By.ID, "checkout"))).click()

    # форма — любые данные
    wait.until(EC.visibility_of_element_located((By.ID, "first-name"))).send_keys("Ivan")
    driver.find_element(By.ID, "last-name").send_keys("Petrov")
    driver.find_element(By.ID, "postal-code").send_keys("123456")
    driver.find_element(By.ID, "continue").click()

    # читаем итог "Total: $58.29"
    total_text = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".summary_total_label"))
    ).text  # напр. "Total: $58.29"

    # вытаскиваем число и сравниваем как Decimal
    # (защищено от проблем с локалями и пробелами)
    amount_str = total_text.split("$")[-1].strip()
    total_val = Decimal(amount_str)
    assert total_val == Decimal("58.29"), f"Ожидали 58.29, получили {total_val}"
