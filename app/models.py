from app import db
from datetime import datetime

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    libraries = db.relationship('Library', backref='record', lazy='dynamic')

    def __repr__(self):
        return '<Record {}>'.format(self.id)

class Library(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    record_id = db.Column(db.Integer, db.ForeignKey('record.id'))
    books = db.relationship('Book', backref='library', lazy='dynamic')

    def __repr__(self):
        return '<Library {}>'.format(self.name)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240))
    ref = db.Column(db.String(120))
    library_id = db.Column(db.Integer, db.ForeignKey('library.id'))

    def __repr__(self):
        return '<Book {}>'.format(self.title)

class BookRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    brn = db.Column(db.Integer)
    title = db.Column(db.String(240))
    author = db.Column(db.String(120))
    classification = db.Column(db.String(120))

    def __repr__(self):
        return '<BookRecord {}:{}>'.format(self.name, self.brn)
