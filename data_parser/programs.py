from collections import OrderedDict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString

from data_parser.base_parser import BaseParser
from validations.schemas.programs_schema import ProgramsSchema


class ProgramsParser(BaseParser):
    link_artsci = "https://fas.calendar.utoronto.ca"
    link_utsc = "https://www.utsc.utoronto.ca/registrar/unlimited-and-limited-programs"
    link_utm = "https://student.utm.utoronto.ca/calendar"

    def __init__(self):
        super().__init__(
            file="../nikel-datasets/data/programs.json",
            schema=ProgramsSchema
        )

    @staticmethod
    def extract_artsci_programs():
        page_number = 0
        programs = []
        while True:
            page = requests.get(f"{ProgramsParser.link_artsci}/search-programs?page={page_number}")
            page_number += 1
            parsed_page = BeautifulSoup(page.content, "lxml")
            title_boxes = parsed_page.find_all("td", {"class": "views-field views-field-title"})
            if len(title_boxes) == 0:
                break
            for title_box in title_boxes:
                anchor = title_box.find("a")
                if anchor is None:
                    continue
                programs.append(anchor["href"])
        return programs

    @staticmethod
    def extract_utm_programs():
        programs = []
        page = requests.get(f"{ProgramsParser.link_utm}/program_list.pl")
        parsed_page = BeautifulSoup(page.content, "lxml")
        anchors = parsed_page.find_all("a", href=True)
        for anchor in anchors:
            if anchor["href"].startswith("program_group.pl"):
                programs.append(anchor["href"])
        return programs

    @staticmethod
    def extract_utsc_programs():
        programs = []
        page = requests.get(ProgramsParser.link_utsc)
        parsed_page = BeautifulSoup(page.content, "lxml")
        tbodies = parsed_page.find_all("tbody")
        for tbody in tbodies[1:]:
            trs = tbody.find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                anchor = tds[0].find("a")
                code = tds[2].text.strip()
                if (anchor["href"] == "http://https://utsc.calendar.utoronto.ca/"
                                      "minor-program-culture-creativity-and-cities-arts"):
                    programs.append(
                        ["https://utsc.calendar.utoronto.ca/minor-program-culture-creativity-and-cities-arts",
                         anchor.text.strip(), code])
                else:
                    programs.append([anchor["href"], anchor.text.strip(), code])
        return programs

    def parse_utm_description(self, element):
        description = ""
        element = element.next_sibling
        while True:
            if isinstance(element, NavigableString):
                description += element.strip(" ") + "\n"
            elif element is None or element.name in ["table", "div"]:
                break
            else:
                description += element.get_text().strip(" ") + "\n"
            element = element.next_sibling
        description = self.sanitize_text(description)
        if description == "":
            return None
        return self.sanitize_text(description)

    @staticmethod
    def get_program_type(program):
        program = program.lower()
        for program_type in ["specialist", "major", "minor", "focus", "certificate"]:
            if program_type in program:
                return program_type
        return None

    @staticmethod
    def remove_prefix(text, prefix):
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    @staticmethod
    def sanitize_text(text):
        return "\n".join(item for item in " ".join(text.split(" ")).split("\n") if item)

    def get_text(self, element, prefixes=None):
        if element is None:
            return None
        res = element.get_text().strip()
        if prefixes is None:
            return res
        for prefix in prefixes:
            if res.startswith(prefix):
                return self.remove_prefix(res, prefix).strip()
        return res

    def process(self):
        print("Processing ART SCI...")
        programs = self.extract_artsci_programs()
        for program in programs:
            page = requests.get(f"{ProgramsParser.link_artsci}{program}")
            parsed_page = BeautifulSoup(page.content, "lxml")
            program_string = parsed_page.find("h1", id="page-title").text.strip()
            program_tuple = program_string.rsplit(" - ", 1)
            if len(program_tuple) != 2:
                continue
            program_type = self.get_program_type(program_tuple[0])
            if program_type is None:
                continue
            description = self.get_text(parsed_page.find("div", {"class": "field-name-field-description"}))
            enrollment = self.get_text(parsed_page.find("div", {"class": "field-name-field-enrolment-requirements"}),
                                       ["Enrolment Requirements:", "Enrolment Requirements"])
            completion = self.get_text(parsed_page.find("div", {"class": "field-name-body"}),
                                       ["Program Requirements:", "Program Requirements"])

            if completion is None or completion == "":
                continue

            date = datetime.now()
            self.add_item(OrderedDict([
                ("id", program_tuple[1]),
                ("name", program_tuple[0]),
                ("type", program_type),
                ("campus", "St. George"),
                ("description", description),
                ("enrollment", enrollment),
                ("completion", completion),
                ("last_updated", date.isoformat())
            ]))

        print("Processing UTM...")
        programs = self.extract_utm_programs()
        for program in programs:
            page = requests.get(f"{ProgramsParser.link_utm}/{program}")
            parsed_page = BeautifulSoup(page.content, "lxml")
            titles = parsed_page.find_all("p", {"class": "title_program"})
            for title in titles:

                for br in title.find_all("br"):
                    # hacky way to allow split by "visual" newline
                    br.replace_with("\n")

                program_name = title.get_text().split("\n")

                if len(program_name) != 2:
                    continue

                program_type, *_, program_code = program_name[0].split()
                program_type = program_type.lower()

                description = self.parse_utm_description(title)

                completion_el = title.find_next("table", {"class": "tab_adm"})
                completion = completion_el.get_text().strip()

                if completion is None:
                    continue

                enrol_el = completion_el.previous_sibling

                if enrol_el.name == "div":
                    enrol = enrol_el.get_text().strip()
                else:
                    enrol = None

                date = datetime.now()
                self.add_item(OrderedDict([
                    ("id", program_code),
                    ("name", program_name[1]),
                    ("type", program_type),
                    ("campus", "Mississauga"),
                    ("description", description),
                    ("enrollment", enrol),
                    ("completion", completion),
                    ("last_updated", date.isoformat())
                ]))

        print("Processing UTSC...")
        programs = self.extract_utsc_programs()
        for program in programs:
            program_type = self.get_program_type(program[1])
            # Exception
            if program_type is None:
                if "Natural Sciences and Environmental Management" in program[1]:
                    program_type = "minor"
                else:
                    input(f"No program type found: {program[1]}")
            page = requests.get(program[0])
            parsed_page = BeautifulSoup(page.content, "lxml")

            description = self.get_text(parsed_page.find("div", {"class": "field-name-field-intro"}))
            enrollment = self.get_text(parsed_page.find("div", {"class": "field-name-field-enrolment-requirements"}),
                                       ["Enrolment Requirements:", "Enrolment Requirements"])
            completion = self.get_text(parsed_page.find("div", {"class": "field-name-body"}),
                                       ["Program Requirements:", "Program Requirements"])

            if completion is None:
                continue

            date = datetime.now()
            self.add_item(OrderedDict([
                ("id", program[2]),
                ("name", program[1]),
                ("type", program_type),
                ("campus", "Scarborough"),
                ("description", description),
                ("enrollment", enrollment),
                ("completion", completion),
                ("last_updated", date.isoformat())
            ]))


if __name__ == "__main__":
    p = ProgramsParser()
    p.run()
