from app.oauth2 import authorize_credentials


def get_calendar_list(credentials):
    """
    Gets all Google Calendar calendars that the user owns
    :param credentials: The Google Calendar API credentials
    :return: A list of Calendars
    """
    service = authorize_credentials(credentials)

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
    print("Adding event")
    cred = event.pop('cred')
    cal_id = event.pop('cal_id')
    service = authorize_credentials(cred)

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
    service = authorize_credentials(cred)
    calendar = {
        'summary': cal_name
    }
    calendar = service.calendars().insert(body=calendar).execute()

    return calendar['id']
