from app import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(200), index=True)
    token = db.Column(db.String(150))
    refresh_token = db.Column(db.String(80))
    token_uri = db.Column(db.String(80))
    client_id = db.Column(db.String(120))
    client_secret = db.Column(db.String(80))
    scopes = db.relationship('Scope', backref='owner', lazy='dynamic')
    calendars = db.relationship('Calendar', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.google_id)


class Calendar(db.Model):
    __tablename__ = 'calendar'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    cal_id = db.Column(db.String(80))
    cal_url = db.Column(db.String(120))
    filters = db.relationship('Filter', backref='owner', lazy='dynamic')


class Filter(db.Model):
    __tablename__ = 'filter'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(80))
    description = db.Column(db.String(300))
    group_name = db.Column(db.String(80))
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendar.id'), index=True)


class Scope(db.Model):
    __tablename__ = 'scope'
    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

