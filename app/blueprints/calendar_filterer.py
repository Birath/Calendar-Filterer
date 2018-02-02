from flask import Blueprint, render_template, request, jsonify, session

from app.calendar_manager import create_google_calendar_from_ical_url
from app.gcal_communication import get_calendar_list

bp = Blueprint('index', __name__)


@bp.route('/')
def render_main():
    if session.get('credentials'):
        calendar_list = get_calendar_list(session['credentials'])
        return render_template('index.html', calendars=calendar_list)
    else:
        return render_template('index.html')


@bp.route('/filterer_test', methods=['POST', 'GET'])
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

    cal = create_google_calendar_from_ical_url(
        cal_url,
        out_calendar_name,
        filters,
        session['credentials']
    )

    return jsonify(cal)
