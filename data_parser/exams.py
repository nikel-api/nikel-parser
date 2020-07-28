from collections import OrderedDict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from data_parser.base_parser import BaseParser
from validations.schemas.exams_schema import ExamsSchema


def get_course_info(month, year, course_code):
    season = course_code[-1]

    endings = {
        'dec': {
            'F': f'{year}9',
            'Y': f'{int(year) - 1}9'
        },
        'apr': {
            'S': f'{year}1',
            'Y': f'{int(year) - 1}9'
        },
        'jun': {
            'F': f'{year}5F',
            'Y': f'{year}5'
        },
        'jul': {
            'S': f'{year}5S',
            'Y': f'{year}5'
        },
        'aug': {
            'S': f'{year}5S',
            'Y': f'{year}5'
        }
    }

    exam_id = course_id = None

    month = month[:3].lower()

    if month in endings and season in endings[month]:
        course_id = f'{course_code}{endings[month][season]}'
        exam_id = f'{course_id}{month.upper()}{year}'

    return exam_id, course_id, course_code


# Currently only supports Art Sci at UTSG
class ExamsParser(BaseParser):
    link_artsci = "https://www.artsci.utoronto.ca/current/faculty-registrar/exams/exam-schedule"
    link_utm = "https://student.utm.utoronto.ca/examschedule/finalexams.php"
    link_utsc = "https://www.utsc.utoronto.ca/registrar/examination-schedule"

    def __init__(self):
        super().__init__(
            file="../nikel-datasets/data/exams.json",
            update=True,
            schema=ExamsSchema
        )

    @staticmethod
    def process_building_code(code):
        for idx, char in enumerate(code):
            if char.isdigit():
                return f"{code[:idx]} {code[idx:]}"
        return code

    def custom_mapping(self, title, fields):
        fields = [field.text.strip() for field in fields]
        if title == "June 2019":
            return [fields[0], fields[1], fields[2], f"{fields[3]} {fields[4]}", fields[5], fields[6], fields[7]]
        elif title == "August 2019":
            return [fields[0], fields[1], fields[2], self.process_building_code(fields[3]), fields[4], fields[5],
                    fields[6]]
        elif title == "December 2019":
            return [fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6]]
        else:
            return [fields[0], fields[1], fields[2], None, fields[3], fields[4], fields[5]]

    def process_utsg(self):
        # Art Sci at UTSG
        page = requests.get(ExamsParser.link_artsci)
        parsed_page = BeautifulSoup(page.content, "lxml")

        terms = parsed_page.find_all("div", {"class": "panel panel-default"})

        for term in terms:
            title = term.find("a", {"class": "accordion-panel-h4-a"}).text
            if title == "Locations":
                continue
            month, year = title.split(" ")
            rows = term.find_all("tr")
            for row in rows[1:]:
                fields = self.custom_mapping(title, row.find_all("td"))
                exam_id, course_id, course_code = get_course_info(month, year, fields[0])

                if exam_id in self.data:
                    split_exists = False
                    for i in range(len(self.data[exam_id]["sections"])):
                        if fields[2] == self.data[exam_id]["sections"][i]["split"]:
                            split_exists = True
                            break
                    if not split_exists:
                        self.data[exam_id]["sections"].append(
                            {
                                "lecture_code": fields[1],
                                "split": fields[2],
                                "location": fields[3]
                            }
                        )
                else:
                    if fields[4] == "Decemberc 10":
                        exam_date = datetime(
                            year=2000,
                            month=12,
                            day=10
                        )
                    else:
                        exam_date = parser.parse(fields[4])

                    date = datetime.now()

                    start_time = parser.parse(fields[5])
                    start_secs = (start_time - start_time.replace(hour=0, minute=0, second=0,
                                                                  microsecond=0)).total_seconds()
                    end_time = parser.parse(fields[6])
                    end_secs = (end_time - end_time.replace(hour=0, minute=0, second=0,
                                                            microsecond=0)).total_seconds()
                    duration = end_secs - start_secs

                    exam = OrderedDict([
                        ("id", exam_id),
                        ("course_id", course_id),
                        ("course_code", course_code),
                        ("campus", "St. George"),
                        ("date", f'{year}-{exam_date.strftime("%m-%d")}'),
                        ("start", int(start_secs)),
                        ("end", int(end_secs)),
                        ("duration", int(duration)),
                        ("sections", [{
                            "lecture_code": fields[1],
                            "split": fields[2],
                            "location": fields[3]
                        }]),
                        ("last_updated", date.isoformat())
                    ])

                    self.add_item(exam)

    def process_utm(self):
        page = requests.get(ExamsParser.link_utm)
        parsed_page = BeautifulSoup(page.content, "lxml")
        # month, year = parsed_page.find("h1").text.split()[:2]
        month, year = ["July", "2020"]
        rows = parsed_page.find_all("tr")
        for row in rows[1:]:
            fields = [field.text.strip() for field in row.find_all("td")]
            exam_id, course_id, course_code = get_course_info(month, year, fields[0])
            exam_date = parser.parse(fields[2])
            start_time = parser.parse(fields[4])
            start_secs = (start_time - start_time.replace(hour=0, minute=0, second=0,
                                                          microsecond=0)).total_seconds()
            end_time = parser.parse(fields[5])
            end_secs = (end_time - end_time.replace(hour=0, minute=0, second=0,
                                                    microsecond=0)).total_seconds()
            duration = end_secs - start_secs

            date = datetime.now()

            exam = OrderedDict([
                ("id", exam_id),
                ("course_id", course_id),
                ("course_code", course_code),
                ("campus", "Mississauga"),
                ("date", f'{year}-{exam_date.strftime("%m-%d")}'),
                ("start", int(start_secs)),
                ("end", int(end_secs)),
                ("duration", int(duration)),
                ("sections", []),
                ("last_updated", date.isoformat())
            ])

            self.add_item(exam)

    def process_utsc(self):
        page = requests.get(ExamsParser.link_utsc)
        parsed_page = BeautifulSoup(page.content, "lxml")
        month, year = parsed_page.find("h2", {"class": "block-title"}).text.split()[:2]
        rows = parsed_page.find_all("tr", {"class": ["odd", "even"]})
        for row in rows:
            fields = [field.text.strip() for field in row.find_all("td")]
            course_code = fields[0].split()[0]
            exam_id, course_id, course_code = get_course_info(month, year, course_code)
            if exam_id is None:
                break
            exam_date = parser.parse(fields[1])

            try:
                start_time = parser.parse(fields[2])
                start_secs = (start_time - start_time.replace(hour=0, minute=0, second=0,
                                                              microsecond=0)).total_seconds()
            except:
                start_time = None
                start_secs = 0

            date = datetime.now()

            if fields[3] == "3:00 +1" or fields[3] == "9:00 +1":
                end_time = start_time
            else:
                end_time = parser.parse(fields[3])

            end_secs = (end_time - end_time.replace(hour=0, minute=0, second=0,
                                                    microsecond=0)).total_seconds()

            duration = end_secs - start_secs

            if duration == 0:
                duration = 3600 * 24

            exam = OrderedDict([
                ("id", exam_id),
                ("course_id", course_id),
                ("course_code", course_code),
                ("campus", "Scarborough"),
                ("date", f'{year}-{exam_date.strftime("%m-%d")}'),
                ("start", int(start_secs)),
                ("end", int(end_secs)),
                ("duration", int(duration)),
                ("sections", []),
                ("last_updated", date.isoformat())
            ])

            self.add_item(exam)

    @staticmethod
    def process_field(page, id: str):
        field = page.find("span", id=id)
        if field:
            field = field.text.strip()
        return field


if __name__ == "__main__":
    p = ExamsParser()
    p.load_file()
    p.process_utsg()
    p.process_utm()
    p.process_utsc()
    p.dump_file()
    p.thread_print(f"Validating {p.file}...")
    p.validate_dump()
