import requests
from selenium import webdriver
import time
from requests.auth import HTTPBasicAuth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome("chromedriver", options=op)
# driver = webdriver.Chrome("chromedriver")


def sign_in(user, passw):
    time.sleep(2)
    cookies_button = driver.find_element_by_xpath(
        '/html/body/div[1]/div/section/div/div[2]/button[2]')
    cookies_button.click()
    time.sleep(2)
    sign_in_link = driver.find_element_by_xpath('/html/body/nav/div/a[2]')
    sign_in_link.click()
    time.sleep(2)
    user_field = driver.find_elements_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[1]/input')[0]
    user_field.send_keys(user)
    passw_field = driver.find_elements_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[2]/input')[0]
    passw_field.send_keys(passw)
    time.sleep(2)
    sign_in_btn = driver.find_elements_by_xpath('//*[@id="organic-div"]/form/div[3]/button')[0]
    sign_in_btn.click()
    try:
        inside = driver.find_elements_by_xpath('//*[@id="ember48"]/div[1]/h1')
    except Exception:
        input("There was a problem logging in, check the browser window pls...")
        time.sleep(5)

def manual_sign_in():
    time.sleep(2)

    cookies_button = driver.find_element_by_xpath(
        '/html/body/div[1]/div/section/div/div[2]/button[2]')
    cookies_button.click()
    time.sleep(2)
    sign_in_link = driver.find_element_by_xpath('/html/body/nav/div/a[2]')
    sign_in_link.click()
    input()


def login():
    driver.get("https://linkedin.com")

    cs = open("pwd.txt").readlines()
    email = cs[0].strip()
    pwd = cs[1].strip()
    print("Signing in...")
    sign_in(email, pwd)

    # manual_sign_in()

    # time.sleep(15)
    time.sleep(5)
    print("Sign in finished!")
    temp_label = ["lang", "bcookie", "bscookie", "li_alerts", "G_ENABLED_IDPS", "li_gc",
                  "li_rm", "AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg", "aam_uuid",
                  "_gcl_au", "li_at", "liap", "JSESSIONID", "li_mc", "lidc", "timezone",
                  "AMCV_14215E3D5995C57C0A495C55%40AdobeOrg"]
    cookies = ''
    csfr = ''

    cooks = driver.get_cookies()

    for j in temp_label:
        for i in cooks:
            if i['name'] == j:
                if i['name'] == "JSESSIONID":
                    csfr = i["value"]
                cookies += f"{j}={i['value']}; "
    cookies = cookies[:len(cookies) - 2]
    driver.close()
    return csfr, f'{cookies}'


csfr, cookies = login()


def get_credentials():
    return csfr, cookies
