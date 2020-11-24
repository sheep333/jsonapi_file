import json
import os
import time
from urllib import request

# import jsonlines
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

BASE_DIR = os.getenv("BASE_DIR", './output/')
RAW_JSON_DIR = os.getenv("RAW_JSON_DIR", "json_outputs/")
DECODE_JSON_DIR = os.getenv("DECODE_JSON_DIR", "decode_json_outputs/")
JSONLINES_DIR = os.getenv("JSONLINES_DIR", "jsonl_outputs/")
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

    # os.makedirs(f"{BASE_DIR}{RAW_JSON_DIR}", exist_ok=True)
    os.makedirs(f"{BASE_DIR}{DECODE_JSON_DIR}", exist_ok=True)
    # os.makedirs(f"{BASE_DIR}{JSONLINES_DIR}", exist_ok=True)

    for element in elements:
        index = 0
        url = element.get_attribute("href")
        if url.startswith(DOMAIN):
            try:
                while url:
                    req = request.Request(f"{url}")
                    split_url = url.split('?')
                    base_url = split_url[0]
                    suffix = base_url.split('/')[-2]
                    file_name = base_url.split('/')[-1]
                    req.add_header("Cookie", f"{cookies[0]['name']}={cookies[0]['value']}")
                    req.add_header("Accept", "application/json")
                    response = request.urlopen(req)
                    print('url:', response.geturl())
                    content = response.read()
                    decode_content = content.decode("utf8")
                    json_content = json.loads(decode_content)
                    # with open(f"{BASE_DIR}{RAW_JSON_DIR}{suffix}__{file_name}_{str(index).zfill(5)}.json", 'wb') as f:
                    #    f.write(content)
                    with open(f"{BASE_DIR}{DECODE_JSON_DIR}{suffix}__{file_name}_{str(index).zfill(5)}.json", 'w') as f:
                        json.dump(json_content, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
                    # with jsonlines.open(f'{BASE_DIR}{JSONLINES_DIR}{file_name}_{str(index).zfill(5)}.jsonl', mode='w') as f:
                    #     f.write(json_content)

                    try:
                        url = json_content["links"]["next"]["href"]
                        index += 1
                    except KeyError:
                        url = None

                    response.close()
            except Exception:
                print(f"Exception raised in url:{url}")
                continue

    driver.quit()


if __name__ == "__main__":
    exec()
