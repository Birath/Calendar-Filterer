import math
from icalendar.parser import unescape_char
from icalendar import Calendar, TypesFactory

from app.gcal_communication import get_calendar_id_from_name,\
    add_event_to_google_calendar, create_new_google_calendar
import requests
import datetime


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


def convert_ical_cal_to_gcal(calendar, filter_fn=None):
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
                google_calendar.append(g_event)
    return google_calendar


def import_calendar_to_gcal(cal_id, calendar, cred):
    """
    Imports a calendar object to the Google Calendar with a ID of cal_id
    :param cal_id: A Google Calendar ID
    :param calendar: A calendar object
    :param cred: The Google Calendar API credentials
    :return: None
    """
    for event in calendar:
        add_event_to_google_calendar(cal_id, event, cred)



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
            course_check.append(course['course_code'] in event['summary'] and
                                course['description'] in event['description'] and not
                                course['group-name'] in event['description'])
        return any(course_check)

    return course_filter


def create_google_calendar_from_ical_url(url, out_name, filters, cred, new_cal):
    ical_cal = get_ICal_calendar(url)
    filters_data = []
    for filter_data in filters:
        filters_data.append(filters[filter_data])

    google_cal = convert_ical_cal_to_gcal(
        ical_cal,
        filter_fn=None
    )

    filtered_cal = convert_ical_cal_to_gcal(
        ical_cal,
        filter_fn=create_filter(filters_data)
    )
    #cal_id = '8njhivg95fij7paf5ek4qhr3ok@group.calendar.google.com'
    if new_cal == "true":
        cal_id = create_new_google_calendar(out_name, cred)
    else:
        cal_id = get_calendar_id_from_name(out_name, cred)

    def import_generator():
        for i, event in enumerate(filtered_cal):
            add_event_to_google_calendar(cal_id, event, cred)
            yield '{}%'.format(math.floor(((i + 1) / len(filtered_cal)) * 100))

    # import_calendar_to_gcal(cal_id, filtered_cal, cred)
    return import_generator


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


if __name__ == '__main__':
    test()



