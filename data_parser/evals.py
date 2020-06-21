import math
import os
import pickle
import re
import time
from collections import OrderedDict
from datetime import datetime
from threading import Thread

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from data_parser.base_parser import BaseParser


def brute_force_regex(text):
    # Make up regexes as you go
    for regex in [
        r"(.*)\s([A-Z]{3}\d+\w\d?)-.*-([A-Z]{3}\d+)",
        r"(.*)([A-Z]{3}\d+\w\d?)-.*-([A-Z]{3}\d+)",
        r"(.*)\s([A-Z]{3}\d+\w\d?)-([A-Z]{3}\d+)",
        r"(.*)([A-Z]{3}\d+\w\d?)-([A-Z]{3}\d+)",
        r"(.*)\s([A-Z]{3}\d+\w\d?)\s-\s([A-Z]{3}\d+)",
        r"(.*)-([A-Z]{3}\d+\w\d?)-([A-Z]{3}\d+)"
    ]:
        course_code_search = re.search(regex, text)
        if course_code_search is not None:
            name = course_code_search.group(1)
            course_code = course_code_search.group(2)
            lecture_code = course_code_search.group(3)
            return name, course_code, lecture_code
    print("WARNING: Unexpected regex failure:", text)
    return "", "", ""


def safe_float_conversion(value):
    if value == "N/A":
        return None
    else:
        return float(value)


def safe_int_conversion(value):
    if value == "N/A":
        return None
    else:
        return int(value)


class EvalsParser(BaseParser):
    link = "https://q.utoronto.ca/courses/48756/external_tools/291"

    def __init__(self):
        super().__init__(
            file="../data/evals.json",
            update=True,
            driver=True
        )

    def process(self):
        self.driver.get(EvalsParser.link)

        # Inject username into username box
        username = self.driver.find_element_by_id("username")
        username.send_keys(os.environ.get('UTOR_USERNAME'))

        # Inject password into password box
        password = self.driver.find_element_by_id("password")
        password.send_keys(os.environ.get('UTOR_PASSWORD'))

        # Trigger login button click
        login = self.driver.find_element_by_css_selector("button")
        login.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "tool_content")))

        self.driver.switch_to.frame(self.driver.find_element_by_id("tool_content"))

        link_box = self.driver.find_element_by_id("launcherElements")
        links = [link.get_attribute("href") for link in link_box.find_elements_by_tag_name("a")]

        for idx, link in enumerate(links):
            self.driver.get(link)

            time.sleep(3)

            pages_left = math.ceil(
                int(self.driver.find_element_by_id("fbvGridNbItemsTotalLvl1").text.split()[1]) / 100
            ) - 1

            # Select show by total
            select_box = self.driver.find_element_by_id("fbvGridPageSizeSelectBlock").find_element_by_tag_name("select")
            show_length = Select(select_box)
            show_length.select_by_index(6)

            index = 1
            while True:
                time.sleep(5)

                table = BeautifulSoup(self.driver.page_source, "html.parser")
                rows = table.find_all("tr", {"class": "gData"})

                for row in rows:
                    fields = [field.text for field in row.find_all("td")]

                    # TODO: FIX THESE MESSED UP MAPPINGS!

                    # Factor-Inwentash School Of Social Work
                    if idx == 0:
                        name, course_code, lecture_code = brute_force_regex(fields[1])

                        if not course_code:
                            continue

                        term = f"{fields[2]} {fields[3]}"

                        lecture = OrderedDict()
                        lecture["lecture_code"] = lecture_code
                        lecture["firstname"] = fields[5]
                        lecture["lastname"] = fields[4]
                        lecture["s1"] = safe_float_conversion(fields[6])
                        lecture["s2"] = safe_float_conversion(fields[7])
                        lecture["s3"] = safe_float_conversion(fields[8])
                        lecture["s4"] = safe_float_conversion(fields[9])
                        lecture["s5"] = safe_float_conversion(fields[10])
                        lecture["s6"] = safe_float_conversion(fields[11])
                        lecture["invited"] = safe_int_conversion(fields[17])
                        lecture["responses"] = safe_int_conversion(fields[18])

                    # Faculty of Applied Science & Engineering (Graduate)
                    elif idx == 1:
                        name, course_code, lecture_code = brute_force_regex(fields[2])

                        if not course_code:
                            continue

                        term = f"{fields[3]} {fields[4]}"

                        lecture = OrderedDict()
                        lecture["lecture_code"] = lecture_code
                        lecture["firstname"] = fields[6]
                        lecture["lastname"] = fields[5]
                        lecture["s1"] = safe_float_conversion(fields[7])
                        lecture["s2"] = safe_float_conversion(fields[8])
                        lecture["s3"] = safe_float_conversion(fields[9])
                        lecture["s4"] = safe_float_conversion(fields[10])
                        lecture["s5"] = safe_float_conversion(fields[11])
                        lecture["s6"] = safe_float_conversion(fields[12])
                        lecture["invited"] = safe_int_conversion(fields[14])
                        lecture["responses"] = safe_int_conversion(fields[15])

                    # Faculty of Applied Science & Engineering (Undergraduate)
                    elif idx == 2:
                        name, course_code, lecture_code = brute_force_regex(fields[2])

                        if not course_code:
                            continue

                        term = f"{fields[3]} {fields[4]}"

                        lecture = OrderedDict()
                        lecture["lecture_code"] = lecture_code
                        lecture["firstname"] = fields[6]
                        lecture["lastname"] = fields[5]
                        lecture["s1"] = safe_float_conversion(fields[7])
                        lecture["s2"] = safe_float_conversion(fields[8])
                        lecture["s3"] = safe_float_conversion(fields[9])
                        lecture["s4"] = safe_float_conversion(fields[10])
                        lecture["s5"] = safe_float_conversion(fields[11])
                        lecture["s6"] = safe_float_conversion(fields[12])
                        lecture["invited"] = safe_int_conversion(fields[21])
                        lecture["responses"] = safe_int_conversion(fields[22])

                    # Faculty of Arts & Science (Undergraduate)
                    elif idx == 3:
                        name, course_code, lecture_code = brute_force_regex(fields[2])

                        if not course_code:
                            continue

                        term = f"{fields[5]} {fields[6]}"

                        lecture = OrderedDict()
                        lecture["lecture_code"] = lecture_code
                        lecture["firstname"] = fields[4]
                        lecture["lastname"] = fields[3]
                        lecture["s1"] = safe_float_conversion(fields[7])
                        lecture["s2"] = safe_float_conversion(fields[8])
                        lecture["s3"] = safe_float_conversion(fields[9])
                        lecture["s4"] = safe_float_conversion(fields[10])
                        lecture["s5"] = safe_float_conversion(fields[11])
                        lecture["s6"] = safe_float_conversion(fields[12])
                        lecture["invited"] = safe_int_conversion(fields[16])
                        lecture["responses"] = safe_int_conversion(fields[17])

                    # Faculty of Information
                    elif idx == 4:
                        name, course_code, lecture_code = brute_force_regex(fields[1])

                        if not course_code:
                            continue

                        term = f"{fields[2]} {fields[3]}"

                        lecture = OrderedDict()
                        lecture["lecture_code"] = lecture_code
                        lecture["firstname"] = fields[5]
                        lecture["lastname"] = fields[4]
                        lecture["s1"] = safe_float_conversion(fields[6])
                        lecture["s2"] = safe_float_conversion(fields[7])
                        lecture["s3"] = safe_float_conversion(fields[8])
                        lecture["s4"] = safe_float_conversion(fields[9])
                        lecture["s5"] = safe_float_conversion(fields[10])
                        lecture["s6"] = safe_float_conversion(fields[11])
                        lecture["invited"] = safe_int_conversion(fields[17])
                        lecture["responses"] = safe_int_conversion(fields[18])

                    # UT Mississauga (Undergraduate)
                    elif idx == 5:
                        name, course_code, lecture_code = brute_force_regex(fields[1])

                        if not course_code:
                            continue

                        term = f"{fields[4]} {fields[5]}"

                        lecture = OrderedDict()
                        lecture["lecture_code"] = lecture_code
                        lecture["firstname"] = fields[3]
                        lecture["lastname"] = fields[2]
                        lecture["s1"] = safe_float_conversion(fields[6])
                        lecture["s2"] = safe_float_conversion(fields[7])
                        lecture["s3"] = safe_float_conversion(fields[8])
                        lecture["s4"] = safe_float_conversion(fields[9])
                        lecture["s5"] = safe_float_conversion(fields[10])
                        lecture["s6"] = safe_float_conversion(fields[11])
                        lecture["invited"] = safe_int_conversion(fields[16])
                        lecture["responses"] = safe_int_conversion(fields[17])

                    # UT Scarborough
                    else:
                        name, course_code, lecture_code = brute_force_regex(fields[1])

                        if not course_code:
                            continue

                        term = f"{fields[2]} {fields[3]}"

                        lecture = OrderedDict()
                        lecture["lecture_code"] = lecture_code
                        lecture["firstname"] = fields[5]
                        lecture["lastname"] = fields[4]
                        lecture["s1"] = safe_float_conversion(fields[6])
                        lecture["s2"] = safe_float_conversion(fields[7])
                        lecture["s3"] = safe_float_conversion(fields[8])
                        lecture["s4"] = safe_float_conversion(fields[9])
                        lecture["s5"] = safe_float_conversion(fields[10])
                        lecture["s6"] = safe_float_conversion(fields[11])
                        lecture["invited"] = safe_int_conversion(fields[15])
                        lecture["responses"] = safe_int_conversion(fields[16])

                    date = datetime.now()

                    if idx == 5:
                        campus = "Mississauga"
                    elif idx == 6:
                        campus = "Scarborough"
                    else:
                        campus = "St. George"

                    # There is bit of redundancy, but it's for safety and robustness
                    if course_code in self.data:
                        term_idx = -1
                        for i in range(len(self.data[course_code]["terms"])):
                            if term == self.data[course_code]["terms"][i]["term"]:
                                term_idx = i
                                break
                        if term_idx != -1:
                            lecture_idx = -1
                            for j in range(len(self.data[course_code]["terms"][term_idx]["lectures"])):
                                if lecture["lecture_code"] == \
                                        self.data[course_code]["terms"][term_idx]["lectures"][j]["lecture_code"]:
                                    lecture_idx = j
                                    break
                            if lecture_idx != -1:
                                self.data[course_code]["terms"][term_idx]["lectures"][lecture_idx] = lecture
                            else:
                                self.data[course_code]["terms"][term_idx]["lectures"].append(lecture)
                        else:
                            term_item = OrderedDict()
                            term_item["term"] = term
                            term_item["lectures"] = [lecture]

                            self.data[course_code]["terms"].append(term_item)

                        self.data[course_code]['last_updated'] = date.isoformat()
                    else:
                        course = OrderedDict()
                        course["id"] = course_code
                        course["name"] = name
                        course["campus"] = campus

                        term_item = OrderedDict()
                        term_item["term"] = term
                        term_item["lectures"] = [lecture]

                        course["terms"] = [term_item]

                        date = datetime.now()
                        course['last_updated'] = date.isoformat()

                        self.add_item(course)

                if pages_left == 0:
                    break

                pages_left -= 1
                index += 1
                self.driver.execute_script(f"__getFbvGrid({index})")

            self.dump_file()
            print(f"Processed {len(self.data)} courses")


if __name__ == "__main__":
    p = EvalsParser()
    p.run()
