import time
import random
import re
from selenium.webdriver.remote.webelement import WebElement

def human_like_type(element: WebElement, text: str) -> None:
    """Escribe texto de forma humana con pausas aleatorias para evadir WAF."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

def clean_filename(name: str) -> str:
    """Elimina caracteres inválidos para nombres de carpetas y archivos en Windows."""
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()
