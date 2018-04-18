from flask import Blueprint, render_template, request, session, jsonify, \
    url_for

from app.db_manager import add_user_to_db, get_credentials, get_user
from app.gcal_communication import get_calendar_list, get_user_id


bp = Blueprint('index', __name__)


@bp.route('/')
def render_main():
    if session.get('credentials'):
        user_id = get_user_id(session['credentials'])
        print("User id:", user_id)
        if not session.get('google_id'):
            if add_user_to_db(user_id, session['credentials']):
                session['google_id'] = user_id
            else:
                session['credentials'] = get_credentials(get_user(user_id))
        else:
            user = get_user(user_id)
            session['credentials'] = get_credentials(user)
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
    new_cal = arguments.pop('new-cal')[0]
    session['cal_url'] = cal_url
    session['out_calendar_name'] = out_calendar_name
    session['new_cal'] = new_cal
    filters = []
    for filter_data in arguments:
        print(arguments[filter_data])
        filters.append({
            "course_code": arguments[filter_data][0],
            "description": arguments[filter_data][1],
            "group_name": arguments[filter_data][2]})
    print(filters)
    session['filters'] = filters
    from app.tasks import upload_cal
    task = upload_cal.delay(
        cal_url,
        out_calendar_name,
        filters,
        session['credentials'],
        new_cal,
        session['google_id']
    )

    return jsonify({}), 202, {'Location': url_for('index.get_progress',
                                                  task_id=task.id)}


@bp.route('/progress<task_id>')
def get_progress(task_id):
    from app.tasks import upload_cal
    task = upload_cal.AsyncResult(task_id)
    print(task.state)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'current': 1,
            'total': 1
        }
    else:
        print(task.info.get('current'))
        print(task.state)
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1)
        }
    return jsonify(response)
