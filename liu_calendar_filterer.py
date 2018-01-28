from flask import Flask, render_template, request, jsonify, redirect, session
from filterer import create_google_calendar_from_ical_url
from authorize_gcal import create_authorization_url, get_credentials

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/filterer_test', methods=['POST', 'GET'])
def filterer():
    cal_url = request.args['calendar-url']
    course_code = request.args['course-code']
    description = request.args['description']
    group_name = request.args['group-name']
    cal = create_google_calendar_from_ical_url(cal_url,
                                               course_code,
                                               description,
                                               group_name,
                                               session['credentials'])

    return jsonify(cal)


@app.route('/start_auth')
def start_ouath():
    authorization_url = create_authorization_url()
    return redirect(authorization_url)


@app.route('/oauth2callback')
def authorize_session():
    credentials = get_credentials(request.url)
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect('/')


if __name__ == '__main__':
    app.config.from_object('config.DevelopmentConfig')
    app.run()
