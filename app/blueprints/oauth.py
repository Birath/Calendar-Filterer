from flask import redirect, session, request, Blueprint

from app.oauth2 import create_authorization_url, get_credentials

bp = Blueprint("oauth", __name__)


@bp.route('/start_auth')
def start_ouath():
    authorization_url = create_authorization_url()
    return redirect(authorization_url)


@bp.route('/oauth2callback')
def authorize_session():
    credentials = get_credentials(request.url)
    session['credentials'] = credentials_to_dict(credentials)

    return redirect('/')


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

