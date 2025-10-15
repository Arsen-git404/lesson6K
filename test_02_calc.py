import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://bonigarcia.dev/selenium-webdriver-java/slow-calculator.html"


@pytest.fixture
def driver():
    opts = ChromeOptions()
    service = ChromeService(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=opts)
    drv.maximize_window()
    yield drv
    drv.quit()


def test_calc_result_after_delay(driver):
    driver.get(URL)

    # ставим задержку 45 сек (локатор #delay)
    delay = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#delay"))
    )
    delay.clear()
    delay.send_keys("45")

    # нажимаем 7 + 8 =
    def click_key(txt: str):
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[normalize-space()='{txt}']"))
        ).click()

    click_key("7")
    click_key("+")
    click_key("8")
    click_key("=")

    # ждём появления результата "15" в экране (div.screen) — до 50 секунд
    WebDriverWait(driver, 50).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "div.screen"), "15")
    )

    # подстрахуемся явным чтением
    screen_text = driver.find_element(By.CSS_SELECTOR, "div.screen").text.strip()
    assert screen_text == "15"
