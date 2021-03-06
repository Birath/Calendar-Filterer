import math
from icalendar.parser import unescape_char
from icalendar import Calendar, TypesFactory

from app.gcal_communication import get_calendar_id_from_name,\
    add_event_to_google_calendar, create_new_google_calendar
from app.db_manager import add_cal_to_user

import requests
import datetime
from multiprocessing import Pool


def utc_to_local(utc_dt):
    """
    Credit to jfs on Stack Overflow
    https://stackoverflow.com/a/13287083
    Converts a datetime object with the utc timezone to one with the timezone
    of the running computer
    :param utc_dt: A datetime object
    :return: A datetime object with the local timezone
    """
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)


def icalendar_to_python(event_properties):
    """
    Converts all properties in a icalendar event to python objects
    :param event_properties: A dictionary with ICalendar event properties
    :return: The same dictionary with all values converted
    """
    converter = TypesFactory()
    for prop in event_properties:
        converted_prop = converter.to_ical(prop, event_properties[prop])
        event_properties[prop] = unescape_char(converted_prop.decode("utf-8"))
    return event_properties


def get_event_properties(event):
    """
    Returns an event's properties as a dictionary
    :param event: An ICalendar event object
    :return: A dictionary with the event properties
    """
    summary = event.get('summary')
    if summary is None:
        return None
    dtstart = event.get('dtstart')
    dtend = event.get('dtend')
    # Converts to local timezone
    start = utc_to_local(dtstart.dt)
    end = utc_to_local(dtend.dt)
    location = event.get('location')
    description = event.get('description')
    uid = event.get('uid')

    event_properties = {
        'summary': summary,
        'start': start.isoformat(),
        'end': end.isoformat(),
        'location': location,
        'description': description,
        'uid': uid
    }

    return icalendar_to_python(event_properties)


def get_calendar(cal_file):
    """
    Returns a ICalendar object based on a ics file
    :param cal_file: An ICS file
    :return: A ICalendar object
    """
    return Calendar.from_ical(cal_file)


def get_ICal_calendar(url):
    """
    Creates a ICalendar object based on the calendar at the url
    :param url: The url to the ICS file
    :return: A ICalendar object
    """
    cal = requests.get(url)
    return get_calendar(cal.content)


def create_google_event(properties):
    """
    Creates a Google Calendar event based on a dictionary with properties
    :param properties: A dictionary with event properties
    :return: A Google Calendar event
    """
    event = {
        'summary': properties['summary'],
        'description': properties['description'],
        'location': properties['location'],
        'start': {
            'dateTime': properties['start']
        },
        'end': {
            'dateTime': properties['end']
        },
        'iCalUID': properties['uid']
    }
    return event


def convert_ical_cal_to_gcal(calendar, cal_id, cred, filter_fn=None):
    """
    Converts a ICal calendar object to a Google Calendar object
    :param calendar: A ICalendar calendar object
    :param filter_fn: A function that determines if an event should be included
    or not
    :return: A Google Calendar object
    """
    google_calendar = []
    for event in calendar.walk():
        event_properties = get_event_properties(event)
        if event_properties is None:
            pass
        else:
            if filter_fn is not None and filter_fn(event_properties):
                pass
            else:
                g_event = create_google_event(event_properties)
                g_event['cal_id'] = cal_id
                g_event['cred'] = cred
                google_calendar.append(g_event)
    return google_calendar


def import_calendar_to_gcal(calendar):
    """
    Imports a calendar object to the Google Calendar with a ID of cal_id
    :param cal_id: A Google Calendar ID
    :param calendar: A calendar object
    :param cred: The Google Calendar API credentials
    :return: None
    """
    for event in calendar:
        add_event_to_google_calendar(event)


def create_filter(courses):
    """
    Creates a function that filters out events in courses
    :param courses: A list of which events should be filtered
    :return: A filter function which takes an event and checks if it should be
    included or not
    """
    def course_filter(event):
        course_check = []
        for course in courses:
            course_check.append(course.course_code in event['summary'] and
                                course.description in event['description'] and not
                                course.group_name in event['description'])
        return any(course_check)

    return course_filter


def create_google_calendar_from_ical_url(url, out_name, filters, cred, new_cal, google_id):
    ical_cal = get_ICal_calendar(url)
    filters_data_list = []
    for filter_data in filters:
        filters_data_list.append(FilterData(
            course_code=filter_data["course_code"],
            description=filter_data["description"],
            group_name=filter_data["group_name"]
        ))

    if new_cal == "true":
        cal_id = create_new_google_calendar(out_name, cred)
    else:
        cal_id = get_calendar_id_from_name(out_name, cred)

    add_cal_to_user(google_id, url, cal_id, filters_data_list)

    filtered_cal = convert_ical_cal_to_gcal(
        ical_cal,
        cal_id,
        cred,
        filter_fn=create_filter(filters_data_list)
    )
    """
    Does NOT work on Windows due to a bug in multiprocessing or flask,
    Probably something to do with this
    https://github.com/pallets/flask/issues/777
    """
    def import_generator():
        """
        A generator which maps all events to pools and import them to google calendar
        :yields: the % of events added
        """
        p = Pool(4)
        #
        for i, event in enumerate(p.imap_unordered(add_event_to_google_calendar, filtered_cal)):
            yield 'data: {}%\n\n'.format(math.floor(((i + 1) / len(filtered_cal)) * 100))
        p.close()
    return filtered_cal
    #return import_generator
    #task = upload_cal.delay(filtered_cal)
    #print(task.AsyncResult(task.request.id).state)


def update_calendar(url, cal_id, filters, cred):
    """
    Updates an existing Google Calendar with the ID cal_id
    :param url: The ICal URL
    :param cal_id: Google Calendar ID
    :param filters: A filter object
    :param cred:
    :return:
    """
    ical_cal = get_ICal_calendar(url)

    filtered_cal = convert_ical_cal_to_gcal(
        ical_cal,
        cal_id,
        cred,
        filter_fn=create_filter(filters)
    )
    import_calendar_to_gcal(filtered_cal)


def test():
    calendar = get_ICal_calendar(
        'https://se.timeedit.net/web/liu/db1/schema/ri6Y7X9QQ6fZ26Qv7509n545yYY06ZQ3Z1Q5708.ics')
    cal_id = 'r3oh0a3vnuqqsd9ppdq57gggb0@group.calendar.google.com'
    course_codes = [{'code': 'TDDE30', 'type': 'Laboration', 'group': 'D1A1'},
                    ]
    g_cal = convert_ical_cal_to_gcal(
        calendar,
        filter_fn=create_filter(course_codes)
    )
    import_calendar_to_gcal(cal_id, g_cal)


class FilterData:
    course_code = ""
    description = ""
    group_name = ""

    def __init__(self, course_code, description, group_name):
        self.course_code = course_code
        self.description = description
        self.group_name = group_name


if __name__ == '__main__':
    test()