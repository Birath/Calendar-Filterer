from app import make_celery, create_app
from app.models import User
from celery.schedules import crontab
from app.calendar_manager import update_calendar, FilterData

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
            filters = []
            for filter_data in user.filters:
                filters.append(FilterData(
                    filter_data.course_code,
                    filter_data.description,
                    filter_data.group_name,
                ))
            cred = {
                'token': user.token,
                'refresh_token': user.refresh_token,
                'token_uri': user.token_uri,
                'client_id': user.client_id,
                'client_secret': user.client_secret,
                'scopes': [user.scopes]
            }
            update_calendar(user.cal_url, user.cal_id, filters, cred)

    print("Finished task")
