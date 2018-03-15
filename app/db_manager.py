from app import db
from app.models import User, Filter, Scope


def add_cal_to_db(google_id, cal_url, cal_id, filters, cred):
    """
    Adds a user to the database
    :param google_id: The users Google ID
    :param cal_url: The url to ical file the user uses
    :param cal_id: The Google Calendar ID the user uses
    :param filters: The users filters
    :param cred: The users credentials
    :return:
    """
    print(cred)
    user = User.query.filter_by(google_id=google_id).first()
    user.cal_id = cal_id
    user.cal_url = cal_url
    user.token = cred['token']
    user.refresh_token = cred['refresh_token']
    user.token_uri = cred['token_uri']
    user.client_id = cred['client_id']
    user.client_secret = cred['client_secret']

    for scope in cred['scopes']:
        scope_object = Scope(scope=scope, owner=user)
        db.session.add(scope_object)

    for cal_filter in filters:
        filter_object = Filter(
            course_code=cal_filter.course_code,
            description=cal_filter.description,
            group_name=cal_filter.group_name,
            owner=user
        )
        db.session.add(filter_object)
    db.session.commit()


def add_user_to_db(google_id):
    """
    Creates a user with the Google ID
    :param google_id: A Google Account ID
    :return: None
    """
    print("Adding user")
    print(User.query.filter_by(google_id=google_id).first())
    if User.query.filter_by(google_id=google_id).first() is None:
        user = User(
            google_id=google_id
        )
        db.session.add(user)
        db.session.commit()
        print("added user")


def get_credentials(google_id):
    """
    Gets the credentials for a google account
    :param google_id:
    :return:
    """
    user = User.query.filter_by(google_id=google_id)
    credentials = {
        'token': user.token,
        'refresh_token': user.refresh_token,
        'token_uri': user.token_uri,
        'client_id': user.client_id,
        'client_secret': user.client_secret,
        'scopes': user.scopes
    }
    return credentials

