"""Creación de instancias de Chrome, Chrome incógnito y Edge."""
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from config import TIMEOUT_PAGINA, URL
from logging_utils import log


def abrir_chrome(index: int):
    options = ChromeOptions()
    profile_path = os.path.abspath(f"./chrome_profile_{index}")
    options.add_argument(f"--user-data-dir={profile_path}")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(TIMEOUT_PAGINA)
    driver.get(URL)
    nombre = f"Chrome-{index}"
    log(f"[OK] {nombre}")
    return driver, nombre


def abrir_chrome_incognito(index: int):
    options = ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(TIMEOUT_PAGINA)
    driver.get(URL)
    nombre = f"Incognito-{index}"
    log(f"[OK] {nombre}")
    return driver, nombre


def abrir_edge(index: int):
    options = EdgeOptions()
    profile_path = os.path.abspath(f"./edge_profile_{index}")
    options.add_argument(f"--user-data-dir={profile_path}")
    driver = webdriver.Edge(options=options)
    driver.set_page_load_timeout(TIMEOUT_PAGINA)
    driver.get(URL)
    nombre = f"Edge-{index}"
    log(f"[OK] {nombre}")
    return driver, nombre
