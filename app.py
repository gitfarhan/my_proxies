from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from subprocess import check_output, CalledProcessError
from urllib.parse import urlparse
import os
import schedule
from pathlib import Path
import signal
import time
from pprint import pprint
import requests
import pymongo
from dotenv import load_dotenv

env = f"{os.getcwd()}/.env"
load_dotenv(env)

MONGO = os.environ.get("MONGO_LOCAL", "mongodb://172.22.0.4:27113/")

devflag = Path(f"{os.getcwd()}/.devflag")

myclient = pymongo.MongoClient(MONGO)
if devflag.exists():
    myclient = pymongo.MongoClient(MONGO)

db = myclient['project_mayhem']
proxies = db['proxies']


def insert_data(data):
    check = check_data(data['ip'], data['port'])
    if check is False:
        print(f"{data['ip']} inserted..")
        return proxies.insert_one(data).acknowledged
    else:
        print(f"{data['ip']} already exists")
        return False

def refresh_proxies():
    check_total_data = len(get_all_data())
    if check_total_data > 20:
        proxies.delete_many({})
        print(f"records clear")

def check_data(ip, port):
    try:
        if proxies.find_one({"$and":[{"ip": ip}, {"port": port}]}):
            return True
        else:
            return False
    except Exception as e:
        print(f"error at check_data: {e}")
        return 0

def get_https_proxy():
    options = Options()
    options.headless = True

    options.add_argument('--disable-gpu')
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    # options.add_argument(f'--proxy-server={PROXY}')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=options)

    url = "https://free-proxy-list.net"

    driver.get(url)

    rows = driver.find_elements_by_class_name("odd")
    result = []
    for row in rows:
        # print(row.text)
        doc = row.text.split(" ")
        if doc[-1].strip().lower() == "yes":
            result.append(dict(
                ip=doc[0],
                port=doc[1],
                code=doc[2],
                anonimity=doc[3],
                https=doc[-1]
            ))

    driver.quit()

    return result

def getPIDs(process):
    try:
        pidlist = map(int, check_output(["pidof", process]).split())
    except CalledProcessError:
        pidlist = []
    return [str(e) for e in pidlist]

def collect():
    refresh_proxies()
    for p in get_https_proxy():
        insert_data(data=p)
    for pid in getPIDs("chromium-browse"):
        os.kill(int(pid), signal.SIGTERM)

def get_all_data():
    result = []
    for data in proxies.find():
        result.append(data)
    return result


schedule.every(10).minutes.do(collect)
while True:
    schedule.run_pending()
    time.sleep(1)
