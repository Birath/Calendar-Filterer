import ssl

from flask import Flask, render_template, request, jsonify, redirect, session
from filterer import create_google_calendar_from_ical_url
from authorize_gcal import create_authorization_url, get_credentials
from gcal_communication import get_calendar_list

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')


@app.route('/')
def render_main():
    if session.get('credentials'):
        calendar_list = get_calendar_list(session['credentials'])
        return render_template('index.html', calendars=calendar_list)
    else:
        return render_template('index.html')


@app.route('/filterer_test', methods=['POST', 'GET'])
def filterer():
    arguments = dict(request.args)
    # All values are stored in lists, which must be removed before use
    cal_url = arguments.pop('calendar-url')[0]
    out_calendar_name = arguments.pop('out-calendar')[0]
    filters = {}
    for filter_data in arguments:
        filter_id = filter_data[-1]
        filter_data_name = filter_data[:-1]
        if filter_data_name == "autocomplete-input":
            filter_data_name = "course_code"
        cur_filter = "filter_{}".format(filter_id)
        if cur_filter in filters:
            filters[cur_filter][filter_data_name] = arguments[filter_data][0]
        else:
            filters[cur_filter] = {filter_data_name: arguments[filter_data][0]}

    cal = create_google_calendar_from_ical_url(cal_url,
                                               out_calendar_name,
                                               filters,
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
    context = ssl.SSLContext()
    context.load_cert_chain("cert.pem", "key.pem")
    app.config.from_object('config.DevelopmentConfig')
    app.run(ssl_context=context)
