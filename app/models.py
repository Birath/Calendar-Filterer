from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(200), index=True)
    cal_id = db.Column(db.String(80))
    cal_url = db.Column(db.String(120))
    token = db.Column(db.String(150))
    refresh_token = db.Column(db.String(80))
    token_uri = db.Column(db.String(80))
    client_id = db.Column(db.String(120))
    client_secret = db.Column(db.String(80))
    scopes = db.relationship('Scope', backref='owner', lazy='dynamic')
    filters = db.relationship('Filter', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}'.format(self.cal_id)


class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(80), index=True)
    description = db.Column(db.String(300))
    group_name = db.Column(db.String(80))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Scope(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

