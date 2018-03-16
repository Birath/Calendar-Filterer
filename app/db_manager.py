from app import db
from app.models import User, Filter, Scope, Calendar


def add_cal_to_user(google_id, cal_url, cal_id, filters):
    """
    Adds a user to the database
    :param google_id: The users Google ID
    :param cal_url: The url to ical file the user uses
    :param cal_id: The Google Calendar ID the user uses
    :param filters: The users filters
    :param cred: The users credentials
    :return:
    """
    user = User.query.filter_by(google_id=google_id).first()
    calendar = Calendar(
        cal_id=cal_id,
        cal_url=cal_url,
        owner=user
    )
    db.session.add(calendar)

    for cal_filter in filters:
        filter_object = Filter(
            course_code=cal_filter.course_code,
            description=cal_filter.description,
            group_name=cal_filter.group_name,
            owner=calendar
        )
        db.session.add(filter_object)
    db.session.commit()


def add_user_to_db(google_id, credentials):
    """
    Creates a user with the Google ID
    :param credentials: The users credentials as a dictionary
    :param google_id: A Google Account ID
    :return: None
    """
    print("Adding user")
    if User.query.filter_by(google_id=google_id).first() is None:
        user = User(
            google_id=google_id
        )
        add_user_credentials(user, credentials)
        db.session.add(user)
        db.session.commit()
        print("added user")
        return user
    else:
        print("User already exist")
        return None


def add_user_credentials(user, credentials):
    user.token = credentials['token']
    user.refresh_token = credentials['refresh_token']
    user.token_uri = credentials['token_uri']
    user.client_id = credentials['client_id']
    user.client_secret = credentials['client_secret']
    for scope in credentials['scopes']:
        scope_object = Scope(
            scope=scope,
            owner=user
        )
        db.session.add(scope_object)


def get_user(google_id):
    return User.query.filter_by(google_id=google_id).first()


def get_credentials(user):
    """
    Gets the credentials for a google account
    :param user: A User object
    :return:
    """
    scopes = []
    for scope in user.scopes:
        scopes.append(scope.scope)
    credentials = {
        'token': user.token,
        'refresh_token': user.refresh_token,
        'token_uri': user.token_uri,
        'client_id': user.client_id,
        'client_secret': user.client_secret,
        'scopes': scopes
    }

    return credentials


def get_calendars(user):
    """
    Gets all the users calendars
    :param user: A user object
    :return: A list of the users calendars
    """
    return [calendar for calendar in user.calendars]
