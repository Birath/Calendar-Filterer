from app import make_celery, create_app
from app.models import User
from celery.schedules import crontab
from app.calendar_manager import update_calendar, FilterData
from app.db_manager import get_credentials

celery = make_celery()
app = create_app()
celery.conf.beat_schedule = {
    'update_cal': {
        'task': 'tasks.update_cal',
        #'schedule': crontab(minute=0, hour="*/2")
        'schedule': crontab()
    }
}


@celery.task(name='tasks.update_cal')
def update_cals():
    print("Updating all calendars...")
    with app.app_context():
        for user in User.query.all():
            print("Updating ", user)
            credentials = get_credentials(user)
            for calendar in user.calendars:
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
