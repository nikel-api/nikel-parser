import re
from collections import OrderedDict
from datetime import datetime
from threading import Thread

import requests
from bs4 import BeautifulSoup

from data_parser.base_parser import BaseParser
from validations.schemas.courses_schema import CoursesSchema


class CoursesParser(BaseParser):
    link = "https://coursefinder.utoronto.ca/course-search/search"

    def __init__(self):
        super().__init__(
            file="../nikel-datasets/data/courses.json",
            schema=CoursesSchema
        )

    def fill_queue(self):
        course_links = self.extract_courses_links()

        for link in course_links:
            self.queue.put(link)

    # This is a complete mess and many crimes have been committed. Will fix later
    def process(self):

        # unique_labels = []

        courses = []

        while not self.queue.empty():
            link = self.queue.get()
            self.thread_print(f"{self.queue.qsize()} Left: {link}")
            page = requests.get(link)
            parsed_page = BeautifulSoup(page.content, "lxml")
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
            title_parse = re.search(r"(.*?): (.*)", title)
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
                                            "lxml")

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

            date = datetime.now()

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
                ("last_updated", date.isoformat()),
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
        courses = []
        sess = requests.Session()

        # set cookies
        sess.get(f"{CoursesParser.link}/courseSearch?viewId=CourseSearch-FormView&methodToCall=start#search")

        resp = sess.get(
            f"{CoursesParser.link}/courseSearch/course/search"
            f"?queryText=&requirements=&campusParam=St.%20George,Scarborough,Mississauga"
        ).json()

        for course in resp["aaData"]:
            link = BeautifulSoup(course[1], 'html.parser')
            courses.append(f'{CoursesParser.link}/{link.find("a")["href"]}')

        return courses


if __name__ == "__main__":
    p = CoursesParser()
    p.load_file()
    p.fill_queue()
    for i in range(p.threads):
        t = Thread(target=p.process, args=())
        t.start()
    p.queue.join()
    p.clean_up()
    p.dump_file()

    p.thread_print(f"Validating {p.file}...")
    p.validate_dump()
