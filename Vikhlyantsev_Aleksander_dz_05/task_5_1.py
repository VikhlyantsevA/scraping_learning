from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv
import time
import os

from my_lib.operators.db_utils import MongodbUtils

load_dotenv()
login = os.getenv("MAIL_LOGIN")
password = os.getenv("MAIL_PASSWORD")

m_utils = MongodbUtils()

options = Options()
options.add_argument("start-maximized")

service = Service("./drivers/chromedriver")
with webdriver.Chrome(service=service, options=options) as driver:
    driver.implicitly_wait(15)

    driver.get("https://mail.ru/")
    driver.find_element(By.XPATH, "//button[contains(@class, 'resplash-btn_primary')]").click()

    iframe = driver.find_element(By.XPATH, "//iframe[contains(@class, 'iframe')]")
    driver.switch_to.frame(iframe)

    elem = driver.find_element(By.NAME, "username")
    elem.send_keys(login)
    elem.send_keys(Keys.ENTER)

    elem = driver.find_element(By.NAME, "password")
    elem.send_keys(password)
    elem.send_keys(Keys.ENTER)

    links = set()
    prev_link = None
    limit = 1
    counter = 0
    while True:
        time.sleep(1)
        mails = driver.find_elements(By.XPATH, "//a[contains(@class,'llc')]")
        last_link = mails[-1].get_attribute('href')
        if last_link == prev_link:
            break

        for mail in mails:
            link = mail.get_attribute('href')
            if not link in links:
                links.add(link)
        actions = ActionChains(driver)
        actions.move_to_element(mails[-1])
        actions.perform()
        prev_link = last_link
        counter += 1

        # Принудительное завершение парсинга писем
        if limit:
            if counter >= limit:
                print('Mails flicking up was completed')
                break

    time.sleep(10)
    # Открытие письма и скрапинг его содержимого
    # Запись res в MongoDB
    print('Start writing to MongoDB')
    for link in links:
        driver.get(link)
        sender_name = driver.find_element(By.XPATH, "//span[contains(@class, 'letter-contact')]").text
        sender_email = driver.find_element(By.XPATH, "//span[contains(@class, 'letter-contact')]").get_attribute(
            "title")
        sent_at = driver.find_element(By.XPATH, "//div[@class='letter__date']").text
        topic = driver.find_element(By.XPATH, "//div[@class='thread__header']//*[@class='thread-subject']").text
        mail_content = driver.find_element(By.XPATH, "//div[@class = 'letter__body']").get_attribute("innerText")

        data = [{
            'sender_name': sender_name,
            'sender_email': sender_email,
            'sent_at': sent_at,
            'topic': topic,
            'mail_content': mail_content
        }]

        m_utils.save_documents('mails', 'mail_ru', data)
        print('Writing to database was successfully completed')

        m_utils.show_documents('mails', 'mail_ru')
