"""
Grabber Utilities - أدوات مساندة (Joiner, Filter, Poll)
"""

import time
import re
import random
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class GrabberUtils:
    """
    Mixin for Group Joiner and Number Filter.
    """

    def group_joiner(self, driver, group_links: List[str]) -> List[str]:
        joined_groups = []
        for i, link in enumerate(group_links, 1):
            try:
                driver.get(link)
                time.sleep(3)
                try:
                    webwait = getattr(
                        __import__("backend.grabber", fromlist=["WebDriverWait"]),
                        "WebDriverWait",
                        WebDriverWait,
                    )
                    join_btn = webwait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "//div[@role='button']//div[contains(text(), 'Join')]",
                            )
                        )
                    )
                    join_btn.click()
                    joined_groups.append(link)
                    time.sleep(random.randint(5, 15))
                except TimeoutException:
                    pass
            except:
                pass
        return joined_groups

    def number_filter(self, driver, numbers: List[str]) -> List[str]:
        valid_numbers = []
        for num in numbers:
            try:
                clean_num = re.sub(r"\D", "", num)
                if not clean_num:
                    continue
                url = f"https://web.whatsapp.com/send?phone={clean_num}"
                driver.get(url)
                try:
                    webwait = getattr(
                        __import__("backend.grabber", fromlist=["WebDriverWait"]),
                        "WebDriverWait",
                        WebDriverWait,
                    )
                    webwait(driver, 10).until(
                        lambda d: d.find_elements(By.CSS_SELECTOR, "#main")
                        or d.find_elements(
                            By.XPATH, "//div[contains(text(), 'invalid')]"
                        )
                    )
                    if driver.find_elements(By.CSS_SELECTOR, "#main"):
                        valid_numbers.append(clean_num)
                except TimeoutException:
                    pass
            except:
                pass
        return valid_numbers
