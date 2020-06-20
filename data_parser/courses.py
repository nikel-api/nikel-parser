import pickle
import re
import time
from collections import OrderedDict
from datetime import datetime
from threading import Thread

import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from data_parser.base_parser import BaseParser


class CoursesParser(BaseParser):
    link = "http://coursefinder.utoronto.ca/course-search/search"

    def __init__(self):
        super().__init__(
            file="../data/courses.json",
            update=True,
            driver=True,
            threads=64
        )

    def fill_queue(self, extract=False):
        if extract:
            self.extract_courses_links()

        with open("../pickles/course_links.pkl", "rb") as f:
            course_links = pickle.load(f)

        for link in course_links:
            self.queue.put(link)

    # This is a complete mess and many crimes have been committed. Will fix later
    def process(self):

        # unique_labels = []

        courses = []

        while not self.queue.empty():
            link = self.queue.get()
            print(f"{self.queue.qsize()} Left: {link}")
            page = requests.get(link)
            parsed_page = BeautifulSoup(page.content, "html.parser")
            inner_page = parsed_page.find("div", id="correctPage")

            if inner_page is None:
                self.queue.task_done()
                continue

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

            if last_updated:
                last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.0").isoformat()

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

            courses.append(OrderedDict([
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
            ]))

            self.queue.task_done()

        self.result_queue.put(courses)

    def clean_up(self):
        while not self.result_queue.empty():
            courses = self.result_queue.get()
            for course in courses:
                self.add_item(course)

    @staticmethod
    def process_field(page, id: str):
        field = page.find("span", id=id)
        if field:
            field = field.text.strip()
        return field

    def extract_courses_links(self):
        self.driver.get(CoursesParser.link)

        # Inject *** wildcard query into search box.
        search_box = self.driver.find_element_by_id("searchQueryId_control")
        search_box.send_keys("***")
        search_box.send_keys(Keys.ENTER)

        # Wait for page to load before continuing
        time.sleep(3)

        # Count courses
        course_number_element = self.driver.find_element_by_id("courseSearchResults_info")
        course_number_search = re.search("Showing 1-20 of (.*) results", course_number_element.text)
        total = int(course_number_search.group(1).replace(",", ""))

        # Select show by total
        select_box = self.driver.find_element_by_name("courseSearchResults_length")
        options = select_box.find_elements_by_tag_name("option")
        self.driver.execute_script("arguments[0].value = arguments[1]", options[3], str(total))

        show_length = Select(select_box)
        show_length.select_by_index(3)

        results_box = self.driver.find_element_by_id("courseSearchResults")
        links = results_box.find_elements_by_css_selector("a[target]")

        print(f"Processing {len(links)} links")

        courses = []

        for idx, link in enumerate(links):
            link_text = link.get_attribute("href")
            if link_text is not None and link_text.startswith(f"{CoursesParser.link}/courseSearch/coursedetails/"):
                courses.append(link_text)

            if idx % 1000 == 999:
                print(f"Processed {idx + 1} links")

        with open("../pickles/course_links.pkl", "wb") as f:
            pickle.dump(courses, f)


if __name__ == "__main__":
    p = CoursesParser()
    p.load_file()
    p.fill_queue(
        extract=True
    )
    for i in range(p.threads):
        t = Thread(target=p.process, args=())
        t.start()
    p.queue.join()
    p.clean_up()
    p.dump_file()
