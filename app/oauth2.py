import google.oauth2.credentials
import google.auth.transport.urllib3
import urllib3
import google_auth_oauthlib.flow

from apiclient import discovery

CLIENT_ID = '807046711232-8g7s3qgri59cc7e9a25ofe0bem71j8bm.apps.googleusercontent.com'
SCOPES = ['https://www.googleapis.com/auth/calendar', 'profile']
CLIENT_SECRET_FILE = 'instance/client_secret_website.json'
APPLICATION_NAME = 'LIU Calendar Filterer'
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
flow.redirect_uri = 'https://127.0.0.1:5000/oauth2callback'


def create_authorization_url():
    """
    Gets the authorization url for Google Oauth2
    :return: A url
    """
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return authorization_url


def get_credentials(response):
    """
    Gets the credentials from the Oauth2 response
    :param response: The response url
    :return: Credentials for connecting to the google API
    """
    flow.fetch_token(authorization_response=response)
    return flow.credentials


def get_gcal_service(credentials):
    """
    Returns an authorized service for the Google Calendar API
    :param credentials: Credentials stored in the flask session
    :return: Authorized service for the Google Calendar API
    """

    credentials = google.oauth2.credentials.Credentials(
        **credentials
    )

    if credentials.expired:
        print("Cred expired")


    http = urllib3.PoolManager()
    request = google.auth.transport.urllib3.Request(http)
    # credentials.refresh(request)
    # request = requests.Request()
    # credentials.refresh(request)
    service = discovery.build(
        'calendar', 'v3',
        credentials=credentials, cache_discovery=False
    )
    return service


def get_user_info_service(credentials):
    """
    Creates an authorized service for the Google People API
    :param credentials: Google API credentials
    :return: Authorized service for the Google People API
    """
    credentials = google.oauth2.credentials.Credentials(
        **credentials
    )
    service = discovery.build(
        serviceName='people', version='v1',
        credentials=credentials, cache_discovery=False,
    )
    return service
