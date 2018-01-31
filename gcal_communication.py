from authorize_gcal import authorize_credentials


def get_calendar_list(credentials):

    service = authorize_credentials(credentials)

    calendar_list = service.calendarList().list(minAccessRole="owner").execute()
    return calendar_list['items']
