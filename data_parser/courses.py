import json
import math
import pickle
import re
import time
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from config.base_urls import BaseURls
from data_parser.base_parser import BaseParser


class CoursesParser(BaseParser):
    def __init__(self):
        super().__init__(BaseURls.COURSES)

    def process(self, extract=False):
        if extract:
            self.extract_courses_links()

        with open("../pickles/course_links.pkl", "rb") as f:
            course_links = pickle.load(f)

        try:
            with open("../data/courses.json", encoding="utf-8") as f:
                courses = json.load(f, object_pairs_hook=OrderedDict)
        except FileNotFoundError:
            courses = OrderedDict()

        # unique_labels = []

        for idx, link in enumerate(course_links):
            course_id = link.rsplit('/', 1)[-1]
            if course_id in courses:
                print(idx + 1)
                continue
            page = requests.get(link)
            parsed_page = BeautifulSoup(page.content, "html.parser")
            inner_page = parsed_page.find("div", id="correctPage")

            # Used for generating new labels

            # labels = inner_page.find_all("label")
            # for label in labels:
            #     if label.text not in unique_labels:
            #         unique_labels.append(label.text)
            #         print(label.text, link)

            title = inner_page.find("span", {"class": "uif-headerText-span"}).text
            title_parse = re.search("(.*): (.*)", title)
            course_id = link.rsplit('/', 1)[-1]
            course_code = title_parse.group(1)
            course_name = title_parse.group(2)
            division = self.process_field(inner_page, "u23")
            description = self.process_field(inner_page, "u32")
            department = self.process_field(inner_page, "u41")
            prerequisites = self.process_field(inner_page, "u50")
            corequisites = self.process_field(inner_page, "u59")
            exclusions = self.process_field(inner_page, "u68")
            recommended_preparation = self.process_field(inner_page, "u77")
            level = self.process_field(inner_page, "u86")
            campus = self.process_field(inner_page, "u149")
            term = self.process_field(inner_page, "u158")
            arts_and_science_breadth = self.process_field(inner_page, "u122")
            arts_and_science_distribution = self.process_field(inner_page, "u131")
            utm_distribution = self.process_field(inner_page, "u113")
            utsc_breadth = self.process_field(inner_page, "u104")
            apsc_electives = self.process_field(inner_page, "u140")
            last_updated = self.process_field(inner_page, "u331")

            # Make use of cobalt's scraper code since
            # I don't have the time to write brand new
            # custom code that's error tolerant.
            meeting_table = inner_page.find("table", id="u172")

            rows = []
            if meeting_table:
                rows = meeting_table.find_all("tr")

            sections = []

            for row in rows:
                tds = row.find_all("td")
                if not tds:
                    continue
                meeting_code = tds[0].text.strip()

                raw_times = tds[1].get_text().replace(
                    "Alternate week", "").strip().split(" ")
                times = []
                for j in range(0, len(raw_times) - 1, 2):
                    times.append(raw_times[j] + " " + raw_times[j + 1])

                instructors = BeautifulSoup(str(tds[2]).replace("<br>", "\n"),
                                            "html.parser")

                instructors = instructors.get_text().split("\n")
                instructors = list(filter(None, [x.strip() for x in instructors]))

                raw_locations = tds[3].get_text().strip().split(" ")
                locations = []
                for j in range(0, len(raw_locations) - 1, 2):
                    locations.append(
                        raw_locations[j] + " " + raw_locations[j + 1])

                try:
                    class_size = int(tds[4].get_text().strip())
                except:
                    class_size = None

                try:
                    current_enrollment = int(tds[5].get_text().strip())
                except:
                    current_enrollment = None

                try:
                    option_to_waitlist = tds[6].find("img", {"src": "../courseSearch/images/checkmark.png"}) is not None
                except:
                    option_to_waitlist = None

                try:
                    delivery_mode = tds[7].text.strip().lower()
                except:
                    delivery_mode = None

                time_data = []
                for j in range(len(times)):
                    info = times[j].split(" ")
                    day = info[0].lower()
                    hours = info[1].split("-")

                    try:
                        location = locations[j]
                    except:
                        location = None

                    for j in range(len(hours)):
                        x = hours[j].split(':')
                        hours[j] = (60 * 60 * int(x[0])) + (int(x[1]) * 60)

                    time_data.append(OrderedDict([
                        ("day", day),
                        ("start", hours[0]),
                        ("end", hours[1]),
                        ("duration", hours[1] - hours[0]),
                        ("location", location)
                    ]))

                data = OrderedDict([
                    ("code", meeting_code),
                    ("instructors", instructors),
                    ("times", time_data),
                    ("size", class_size),
                    ("enrollment", current_enrollment),
                    ("waitlist_option", option_to_waitlist),
                    ("delivery", delivery_mode)
                ])

                sections.append(data)

            courses[course_id] = OrderedDict([
                ("id", course_id),
                ("code", course_code),
                ("name", course_name),
                ("description", description),
                ("division", division),
                ("department", department),
                ("prerequisites", prerequisites),
                ("corequisites", corequisites),
                ("exclusions", exclusions),
                ("recommended_preparation", recommended_preparation),
                ("level", level),
                ("campus", campus),
                ("term", term),
                ("arts_and_science_breadth", arts_and_science_breadth),
                ("arts_and_science_distribution", arts_and_science_distribution),
                ("utm_distribution", utm_distribution),
                ("utsc_breadth", utsc_breadth),
                ("apsc_electives", apsc_electives),
                ("meeting_sections", sections),
                ("last_updated", last_updated),
            ])

            if idx % 100 == 99:
                with open("../data/courses.json", "w", encoding="utf-8") as f:
                    json.dump(courses, f, ensure_ascii=False)

            print(idx + 1)

        with open("../data/courses.json", "w", encoding="utf-8") as f:
            json.dump(courses, f, ensure_ascii=False)

    @staticmethod
    def process_field(page, id: str):
        field = page.find("span", id=id)
        if field:
            field = field.text.strip()
        return field

    def extract_courses_links(self):
        self.driver.get(self.base_url)

        # Inject *** wildcard query into search box.
        search_box = self.driver.find_element_by_id("searchQueryId_control")
        search_box.send_keys("***")
        search_box.send_keys(Keys.ENTER)

        # Wait for page to load before selection
        time.sleep(3)

        # Select show by 100
        show_length = Select(self.driver.find_element_by_name("courseSearchResults_length"))
        show_length.select_by_index(3)

        # Wait for page to extract links
        time.sleep(3)

        # Count pages left
        course_number_element = self.driver.find_element_by_id("courseSearchResults_info")
        course_number_search = re.search("Showing 1-100 of (.*) results", course_number_element.text)
        pages_left = math.ceil(int(course_number_search.group(1).replace(",", "")) / 100)

        # Get next button
        next_button = self.driver.find_element_by_id("courseSearchResults_next")

        courses = []

        while True:
            links = self.driver.find_elements_by_xpath("//a[@href]")

            for link in links:
                link_text = link.get_attribute("href")
                if link_text.startswith(f"{self.base_url}/courseSearch/coursedetails/"):
                    courses.append(link_text)

            if pages_left == 0:
                break

            pages_left -= 1
            next_button.click()

        with open("../pickles/course_links.pkl", "wb") as f:
            pickle.dump(courses, f)


if __name__ == "__main__":
    p = CoursesParser()
    p.process()
