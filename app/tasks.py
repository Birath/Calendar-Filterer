from app import celery
from .models import User
from .calendar_manager import update_calendar, FilterData, create_google_calendar_from_ical_url
from .gcal_communication import add_event_to_google_calendar
from .db_manager import get_credentials
from celery.schedules import crontab
celery.conf.beat_schedule = {
    'update_cal': {
        'task': 'tasks.update_cal',
        'schedule': crontab(minute=0, hour="*/2")
        #'schedule': crontab()
    }
}


@celery.task(name='tasks.update_cal')
def update_cals():
    print("Updating all calendars...")
    for user in User.query.all():
        print("Updating ", user)
        credentials = get_credentials(user)
        for calendar in user.calendars:
            print("Updating calendar", calendar.cal_id)
            filters = []
            for filter_data in calendar.filters:
                filters.append(FilterData(
                    filter_data.course_code,
                    filter_data.description,
                    filter_data.group_name,
                ))
            update_calendar(
                calendar.cal_url,
                calendar.cal_id,
                filters,
                credentials
            )

    print("Finished task")


@celery.task(bind=True)
def upload_cal(self, url, out_name, filters, cred, new_cal, google_id):
    calendar = create_google_calendar_from_ical_url(
        url,
        out_name,
        filters,
        cred,
        new_cal,
        google_id
    )
    for i, event in enumerate(calendar):
        add_event_to_google_calendar(event)
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': len(calendar)})
    #import_calendar_to_gcal(calendar)