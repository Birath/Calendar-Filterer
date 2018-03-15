from app.oauth2 import get_gcal_service, get_user_info_service


def get_calendar_list(credentials):
    """
    Gets all Google Calendar calendars that the user owns
    :param credentials: The Google Calendar API credentials
    :return: A list of Calendars
    """
    service = get_gcal_service(credentials)

    calendar_list = service.calendarList().list(
        minAccessRole="owner"
    ).execute()
    return calendar_list['items']


def get_calendar_id_from_name(cal_name, credentials):
    """
    Gets the Google Calendar ID based on the name of the calendar
    :param cal_name: The calendars name
    :param credentials: The Google Calendar API credentials
    :return: A Google Calendar ID
    """
    cal_list = get_calendar_list(credentials)

    for calendar in cal_list:
        if calendar['summary'] == cal_name:
            return calendar['id']


def add_event_to_google_calendar(event):
    """
    Adds an event to the google calendar with the id cal_id
    :param cal_id: A Google Calendar ID
    :param event: A Google Calendar event
    :param cred: The Google Calendar API credentials
    :return:
    """
    cred = event.pop('cred')
    cal_id = event.pop('cal_id')
    service = get_gcal_service(cred)

    imported_event = service.events().import_(
        calendarId=cal_id,
        body=event
    ).execute()


def create_new_google_calendar(cal_name, cred):
    """
    Creates a Google Calendar with cal name
    :param cal_name: The calendars name
    :param cred: The Google Calendar API credentials
    :return: The created calendars id
    """
    service = get_gcal_service(cred)
    calendar = {
        'summary': cal_name
    }
    calendar = service.calendars().insert(body=calendar).execute()

    return calendar['id']


def get_user_id(cred):
    """
    Gets the user id
    :param cred: Google API credentials
    :return: The user id
    """
    service = get_user_info_service(cred)
    user_info = service.people().get(
        resourceName='people/me', personFields='metadata'
    ).execute()
    # User id is for some reason in a list under sources
    user_id = user_info['metadata']['sources'][0]['id']
    return user_id
