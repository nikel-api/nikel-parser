import re
import time
from collections import OrderedDict
from datetime import datetime
from threading import Thread

import requests
from bs4 import BeautifulSoup

from data_parser.base_parser import BaseParser


# Make full use of cobalt's existing code
class TextbooksParser(BaseParser):
    link = "https://uoftbookstore.com"

    # currently redundant
    campus_map = {
        "utsg": "St. George",
        "utm": "Mississauga",
        "utsc": "Scarborough"
    }

    def __init__(self):
        super().__init__(
            file="../data/textbooks.json",
            threads=10
        )

    def fill_queue(self):
        terms = self.retrieve_terms()
        departments = self.retrieve_departments(terms)

        for department in departments:
            self.queue.put(department)

    def process(self):
        textbooks = []

        while not self.queue.empty():
            # Sleep to prevent servers from freaking out
            time.sleep(5)
            department = self.queue.get()
            self.thread_print(f"{self.queue.qsize()} Left: {department}")
            courses = self.retrieve_courses(department)
            for course in courses:
                sections = self.retrieve_sections(course)
                for section in sections:
                    books = self.retrieve_books(section)
                    for book in books:
                        textbooks.append(book)
            self.queue.task_done()

        self.result_queue.put(textbooks)

    def clean_up(self):
        while not self.result_queue.empty():
            textbooks = self.result_queue.get()
            for textbook in textbooks:
                self.add_item(textbook)

    @staticmethod
    def process_field(el, field):
        if field in el:
            return el[field]
        return None

    @staticmethod
    def process_attributes(mapping, attributes):
        res = []
        for attribute in mapping:
            if attribute['id'] in attributes:
                res.append(attribute['title'])
        return res

    def retrieve_terms(self):
        try:
            html = requests.get(f'{TextbooksParser.link}/buy_courselisting.asp', timeout=60)
        except requests.exceptions.Timeout:
            return []

        if html is None:
            return []

        listing = BeautifulSoup(html.content, "lxml")

        terms = listing.find(id='fTerm').find_all('option')[1:]

        accepted_terms = []
        for term in terms:
            val = term.get_text()
            if val.startswith('ST GEORGE') or val.startswith('MISSISSAUGA') \
                    or val.startswith('SCARBOROUGH'):
                accepted_terms.append(term)

        return accepted_terms

    def retrieve_departments(self, terms):
        all_departments = []

        for term in terms:
            term_name = term.get_text()
            m = re.search(r'(\d{5})', term_name)
            session = m.group(0)

            campus, term_id = term.get('value').split('|')
            payload = {
                'control': 'campus',
                'campus': campus,
                'term': term_id,
                't': int(round(time.time() * 1000))
            }
            headers = {
                'Referer': f'{TextbooksParser.link}/buy_courselisting.asp'
            }

            try:
                xml = requests.get(f'{TextbooksParser.link}/textbooks_xml.asp', params=payload, headers=headers,
                                   timeout=60)
            except:
                continue

            if xml is None:
                continue

            departments = BeautifulSoup(xml.content, "xml").find_all('department')
            for department in departments:
                all_departments.append({
                    'dept_id': department.get('id'),
                    'dept_name': department.get('name').title(),
                    'term_id': term_id,
                    'session': session
                })

        return all_departments

    def retrieve_courses(self, department):
        all_courses = []

        payload = {
            'control': 'department',
            'dept': department['dept_id'],
            'term': department['term_id'],
            't': int(round(time.time() * 1000))
        }
        headers = {
            'Referer': f'{TextbooksParser.link}/buy_courselisting.asp'
        }

        try:
            xml = requests.get(f'{TextbooksParser.link}/textbooks_xml.asp',
                               params=payload, headers=headers, timeout=60)
        except:
            return []

        if xml is None:
            return []

        courses = BeautifulSoup(xml.content, "xml").find_all('course')
        for course in courses:
            all_courses.append({
                'course_id': course.get('id'),
                'course_name': course.get('name'),
                'term_id': department['term_id'],
                'session': department['session']
            })

        return all_courses

    def retrieve_sections(self, course):
        all_sections = []

        payload = {
            'control': 'course',
            'course': course['course_id'],
            'term': course['term_id'],
            't': int(round(time.time() * 1000))
        }
        headers = {
            'Referer': f'{TextbooksParser.link}/buy_courselisting.asp'
        }

        try:
            xml = requests.get(f'{TextbooksParser.link}/textbooks_xml.asp',
                               params=payload, headers=headers, timeout=60)
        except:
            return []

        if xml is None:
            return []

        sections = BeautifulSoup(xml.content, "xml").find_all('section')
        for section in sections:
            all_sections.append({
                'section_id': section.get('id'),
                'section_code': section.get('name'),
                'section_instructor': section.get('instructor'),
                'course_code': course['course_name'],
                'session': course['session']
            })

        return all_sections

    def retrieve_books(self, section):
        all_books = []

        payload = {
            'control': 'section',
            'section': section['section_id'],
            't': int(round(time.time() * 1000))
        }

        headers = {
            'Referer': f'{TextbooksParser.link}/buy_courselisting.asp'
        }

        try:
            html = requests.get(f'{TextbooksParser.link}/textbooks_xml.asp', params=payload, headers=headers,
                                timeout=60)
        except:
            return []

        if html is None:
            return []

        soup = BeautifulSoup(html.content, "lxml")
        books = soup.find_all('tr', {'class': 'book'})

        if books is None:
            return []

        for book in books:
            if len(book.get_text().strip()) == 0:
                continue

            image = book.find(class_='book-cover').img.get('src')
            image = 'http://uoftbookstore.com/%s' % image
            image = image.replace('Size=M', 'Size=L')

            # This doesn't mean "avoid textbooks with no image"
            # This is a case when the textbook is called "No required text"
            if 'not_available_' in image:
                continue

            book_id = book.find(class_='product-field-pf_id').get('value')

            url = f'{TextbooksParser.link}/buy_book_detail.asp?pf_id={book_id}'

            title = self.get_text_from_class(book, 'book-title')

            edition = self.get_text_from_class(book, 'book-edition')
            if len(edition) > 0:
                edition = ''.join(list(filter(str.isdigit, edition)))
                try:
                    edition = int(edition)
                except ValueError:
                    edition = 1
            if edition == '' or 0:
                edition = 1

            author = self.get_text_from_class(book, 'book-author')
            m = re.search(r'([\d]+[E]?)', author)
            if m is not None:
                junk = m.group(0)
                author = author.replace(junk, '').strip()

            isbn = self.get_text_from_class(book, 'isbn')
            requirement = self.get_text_from_class(book, 'book-req')
            requirement = requirement.lower()

            price = self.get_text_from_class(book, 'book-price-list')
            try:
                price = float(price[1:])
            except ValueError:
                price = 0

            instructor = section['section_instructor'].split(',')
            if len(instructor) == 2:
                instructor = '%s %s' % (
                    instructor[0][:1],
                    instructor[1].strip()
                )
                instructor = instructor.strip()
            else:
                instructor = ''

            instructors = [instructor]
            if len(instructor) == 0:
                instructors = []

            meeting_sections = [OrderedDict([
                ("code", section['section_code']),
                ("instructors", instructors)
            ])]

            course_id = '%s%s' % (section['course_code'], section['session'])

            courses = [OrderedDict([
                ("id", course_id),
                ("code", section['course_code']),
                ("requirement", requirement),
                ("meeting_sections", meeting_sections)
            ])]

            date = datetime.now()

            textbook = OrderedDict([
                ("id", book_id),
                ("isbn", isbn),
                ("title", title),
                ("edition", edition),
                ("author", author),
                ("image", image),
                ("price", price),
                ("url", url),
                ("courses", courses),
                ("last_updated", date.isoformat())
            ])

            all_books.append(textbook)

        return all_books

    @staticmethod
    def get_text_from_class(soup, name):
        obj = soup.find(class_=name)
        if obj is not None:
            return obj.get_text().replace('\xa0', ' ').strip()
        else:
            return ''


if __name__ == "__main__":
    p = TextbooksParser()
    p.load_file()
    p.fill_queue()
    for i in range(p.threads):
        t = Thread(target=p.process, args=())
        t.start()
    p.queue.join()
    p.clean_up()
    p.dump_file()
