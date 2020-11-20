import json
import os
import time
from urllib import request

import jsonlines
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

BASE_DIR = os.getenv("BASE_DIR", './output/')
DOMAIN = os.getenv("DOMAIN")
NAME = os.getenv("NAME")
PASS = os.getenv("PASS")
API_PATH = os.getenv("API_PATH")


def exec():
    # bs4でよかったかもしれない...
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_extension('./0.0.32.3_0.crx')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(DOMAIN)
    driver.set_window_size(1440, 877)
    driver.find_element(By.LINK_TEXT, "ログイン").click()
    WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.ID, "edit-name")))
    time.sleep(2)
    driver.find_element(By.ID, "edit-name").click()
    driver.find_element(By.ID, "edit-name").send_keys(NAME)
    driver.find_element(By.ID, "edit-pass").send_keys(PASS)
    driver.find_element(By.ID, "edit-submit").click()
    WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.ID, "toolbar-administration")))
    driver.get(f"{DOMAIN}{API_PATH}")
    cookies = driver.get_cookies()
    print(cookies)
    WebDriverWait(driver, 30).until(expected_conditions.presence_of_element_located((By.TAG_NAME, "a")))
    elements = driver.find_elements_by_css_selector("a")

    json_path = "json_outputs/"
    os.makedirs(f"{BASE_DIR}{json_path}", exist_ok=True)
    decode_json_path = "decode_json_outputs/"
    os.makedirs(f"{BASE_DIR}{decode_json_path}", exist_ok=True)
    jsonl_path = "jsonl_outputs/"
    os.makedirs(f"{BASE_DIR}{jsonl_path}", exist_ok=True)

    for element in elements:
        url = element.get_attribute("href")
        if url.startswith(DOMAIN):
            try:
                req = request.Request(f"{url}")
                req.add_header("Cookie", f"{cookies[0]['name']}={cookies[0]['value']}")
                req.add_header("Accept", "application/json")
                response = request.urlopen(req)
                print('url:', response.geturl())
                content = response.read()
                decode_content = content.decode("utf8")
                suffix = url.split('/')[-2]
                file_name = url.split('/')[-1]
                with open(f"{BASE_DIR}{json_path}{suffix}__{file_name}.json", 'wb') as f:
                    f.write(content)
                with open(f"{BASE_DIR}{decode_json_path}{suffix}__{file_name}.json", 'w') as f:
                    json_content = json.loads(decode_content)
                    json.dump(json_content, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
                with jsonlines.open(f'{BASE_DIR}{jsonl_path}{file_name}.jsonl', mode='w') as f:
                    json_content = json.loads(decode_content)
                    f.write(json_content)
                response.close()
            except Exception:
                print(f"Exception raised in url:{url}")
                continue

    driver.quit()


if __name__ == "__main__":
    exec()
