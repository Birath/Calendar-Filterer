from icalendar.parser import unescape_char
from icalendar import Calendar, TypesFactory

from authorize_gcal import authorize_credentials
from gcal_communication import get_calendar_id_from_name
import requests
import datetime


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json


def utc_to_local(utc_dt):
    """
    Credit to jfs on Stack Overflow
    https://stackoverflow.com/a/13287083
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
    :param event: An icalendar event object
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


def get_timeedit_calendar(url):
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


def add_event_to_google_calendar(cal_id, event, cred):
    """
    Adds an event to the google calendar with the id cal_id
    :param cal_id: A Google Calendar ID
    :param event: A Google Calendar event
    :return:
    """
    service = authorize_credentials(cred)

    imported_event = service.events().import_(calendarId=cal_id,
                                              body=event).execute()


def convert_timeedit_to_gcal(calendar, filter_fn=None):
    """
    Converts a timeedit calendar to a google_calendar
    :param calendar:
    :param filter_fn:
    :return:
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
    for event in calendar:
        add_event_to_google_calendar(cal_id, event, cred)


def create_filter(courses):
    """
    Creates a function that filters out events in courses
    :param courses: A list of which events should be filtered
    :return: A filter function which takes an event and checks if it should be
    filtered or not
    """
    def course_filter(event):
        course_check = []
        for course in courses:
            course_check.append(course['course_code'] in event['summary'] and
                                course['description'] in event['description'] and not
                                course['group-name'] in event['description'])
        return any(course_check)

    return course_filter


def create_google_calendar_from_ical_url(url, out_name, filters, cred):
    timeedit_cal = get_timeedit_calendar(url)
    filters_data = []
    for filter in filters:
        filters_data.append(filters[filter])
    print(filters_data)
    google_cal = convert_timeedit_to_gcal(
        timeedit_cal,
        filter_fn=None
    )
    filterd_cal = convert_timeedit_to_gcal(
        timeedit_cal,
        filter_fn=create_filter(filters_data)
    )
    #cal_id = '8njhivg95fij7paf5ek4qhr3ok@group.calendar.google.com'
    cal_id = get_calendar_id_from_name(out_name, cred)
    import_calendar_to_gcal(cal_id, filterd_cal, cred)
    return google_cal


def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    # cal_id = 't3lk5jdu5gol1m1ugf05kcvtmrm4lgh3@import.calendar.google.com'
    cal_id = 'p9pi74ns63ksuth8lb30d57i88@group.calendar.google.com'
    eventsResult = service.events().list(
        calendarId=cal_id, timeMin=now, maxResults=250, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    course_codes = [{'code': 'TDDE30', 'type': 'Laboration', 'group': 'D1A1'},
                    ]
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))

        for course in course_codes:
            if (course['code'] in event['summary'] and
                    course['type'] in event['description']):
                if not course['group'] in event['description']:
                    print(start, event['summary'])
                    service.events().delete(calendarId=cal_id,
                                            eventId=event['id']).execute()


if __name__ == '__main__':
    # main()
    calendar = get_timeedit_calendar('https://se.timeedit.net/web/liu/db1/schema/ri6Y7X9QQ6fZ26Qv7509n545yYY06ZQ3Z1Q5708.ics')
    cal_id = 'r3oh0a3vnuqqsd9ppdq57gggb0@group.calendar.google.com'
    course_codes = [{'code': 'TDDE30', 'type': 'Laboration', 'group': 'D1A1'},
                    ]
    g_cal = convert_timeedit_to_gcal(calendar,
                                     filter_fn=create_filter(course_codes))
    # import_calendar_to_gcal(cal_id, g_cal)


