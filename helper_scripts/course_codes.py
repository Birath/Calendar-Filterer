import requests
import json
from bs4 import BeautifulSoup


def main():
    response = requests.get('https://liu.se/studieinfo/?type=Course&term=&take=10000')

    soup = BeautifulSoup(response.content, 'html.parser')

    courses = soup.find_all('div', class_='study-guide-search-result-row')
    course_codes = {}
    for course in courses:
        course_code = course.a.h3.text
        course_code = course_code.split(" ")[0]
        course_codes[course_code] = None

    with open("course_data.json", "w+") as f:
        json.dump(course_codes, f)


if __name__ == '__main__':
    main()
