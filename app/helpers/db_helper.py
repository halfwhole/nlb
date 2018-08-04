from app import db
from app.models import Record, Library, Book, BookRecord
from collections import defaultdict

def db_retrieve_avail_libs_dict(record_name):
    avail_libs_dict = defaultdict(list)
    record = Record.query.filter_by(name=record_name).first()
    if not record:
        raise LookupError('Record for record_name={} not found'.format(record_name))
    libraries = record.libraries
    for library in libraries:
        books = library.books
        for book in books:
            avail_libs_dict[library.name].append((book.title, book.ref))
    return dict(avail_libs_dict)

def db_update_avail_libs_dict(avail_libs_dict, record_name):
    db_nuke_avail_libs_dict(record_name)
    db_record = Record(name=record_name)
    db.session.add(db_record)
    db.session.flush()
    for library, books in avail_libs_dict.items():
        db_library = Library(name=library, record_id=db_record.id)
        db.session.add(db_library)
        db.session.flush()
        for book, reference in books:
            db_book = Book(title=book, ref=reference, library_id=db_library.id)
            db.session.add(db_book)
    db.session.commit()

def db_nuke_avail_libs_dict(record_name):
    """Delete any pre-existing Record(s) with name = record_name."""
    records = Record.query.filter_by(name=record_name).all()
    for record in records:
        for library in record.libraries:
            for book in library.books:
                db.session.delete(book)
            db.session.delete(library)
        db.session.delete(record)
    db.session.commit()

def db_retrieve_last_updated(record_name):
    record = Record.query.filter_by(name=record_name).first()
    if not record:
        raise LookupError('Record for record_name={} not found'.format(record_name))
    return record.timestamp

def db_retrieve_book_records(record_name):
    book_records = []
    db_book_records = BookRecord.query.filter_by(name=record_name).all()
    for db_book_record in db_book_records:
        book_record = {}
        book_record['brn'] = db_book_record.brn
        book_record['title'] = db_book_record.title
        book_record['author'] = db_book_record.author
        book_record['classification'] = db_book_record.classification
        book_records.append(book_record)
    return book_records

def db_update_book_records(book_records, record_name):
    db_nuke_book_records(record_name)
    for book_record in book_records:
        db_book_record = BookRecord(name=record_name,
                                    brn=book_record['brn'],
                                    title=book_record['title'],
                                    author=book_record['author'],
                                    classification=book_record['classification'])
        db.session.add(db_book_record)
    db.session.commit()

def db_nuke_book_records(record_name):
    """Delete any pre-existing BookRecord(s) with name = record_name."""
    book_records = BookRecord.query.filter_by(name=record_name).all()
    for book_record in book_records:
        db.session.delete(book_record)
    db.session.commit()
