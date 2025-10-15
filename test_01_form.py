import os
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager


URL = "https://bonigarcia.dev/selenium-webdriver-java/data-types.html"


EDGE_DRIVER = r"C:\Users\arsen\OneDrive\Рабочий стол\msedgedriver.exe"


@pytest.fixture
def driver():
    options = webdriver.EdgeOptions()
    # создаём сервис
    if os.path.exists(EDGE_DRIVER):
        service = EdgeService(executable_path=EDGE_DRIVER)
    else:
        service = EdgeService(EdgeChromiumDriverManager().install())

    drv = webdriver.Edge(service=service, options=options)
    drv.maximize_window()
    drv.implicitly_wait(4)
    yield drv
    drv.quit()


def test_form(driver):
    driver.get(URL)

    # заполняем поля (внимание на точные name с этой страницы)
    driver.find_element(By.CSS_SELECTOR, "[name='first-name']").send_keys("Иван")
    driver.find_element(By.CSS_SELECTOR, "[name='last-name']").send_keys("Петров")
    driver.find_element(By.CSS_SELECTOR, "[name='address']").send_keys("Ленина, 55-3")
    driver.find_element(By.CSS_SELECTOR, "[name='e-mail']").send_keys("test@skypro.com")
    driver.find_element(By.CSS_SELECTOR, "[name='phone']").send_keys("+7985899998787")
    driver.find_element(By.CSS_SELECTOR, "[name='city']").send_keys("Москва")
    driver.find_element(By.CSS_SELECTOR, "[name='country']").send_keys("Россия")
    driver.find_element(By.CSS_SELECTOR, "[name='job-position']").send_keys("QA")
    driver.find_element(By.CSS_SELECTOR, "[name='company']").send_keys("SkyPro")
    # zip-code оставляем пустым

    # submit
    driver.find_element(By.CSS_SELECTOR, ".btn.btn-outline-primary").click()

    # ждём появления success-алерта как маркера, что страница применила классы валидации
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert.alert-success"))
    )

    # 1) Zip должен быть НЕвалидным (класс is-invalid или aria-invalid="true")
    zip_el = driver.find_element(By.CSS_SELECTOR, "[name='zip-code'], #zip-code, [name='zip']")
    zip_cls = zip_el.get_attribute("class") or ""
    zip_aria = (zip_el.get_attribute("aria-invalid") or "").lower()
    assert ("is-invalid" in zip_cls) or (zip_aria == "true"), "Поле Zip code не подсветилось как невалидное"

    # 2) Остальные поля должны быть валидными (is-valid)
    ok_names = [
        "first-name", "last-name", "address", "e-mail",
        "phone", "city", "country", "job-position", "company"
    ]
    for name_attr in ok_names:
        el = driver.find_element(By.CSS_SELECTOR, f"[name='{name_attr}']")
        cls = el.get_attribute("class") or ""
        assert "is-valid" in cls, f"Поле {name_attr} не стало валидным (зелёным)"
