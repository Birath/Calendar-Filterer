from authorize_gcal import authorize_credentials


def get_calendar_list(credentials):

    service = authorize_credentials(credentials)

    calendar_list = service.calendarList().list(minAccessRole="owner").execute()
    return calendar_list['items']


def get_calendar_id_from_name(cal_name, credentials):
    cal_list = get_calendar_list(credentials)

    for calendar in cal_list:
        if calendar['summary'] == cal_name:
            return calendar['id']
