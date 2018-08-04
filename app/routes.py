from flask import render_template, flash, redirect, session

from app import app
from app.forms import AddForm, DeleteForm, LoginForm
from app.helpers.libs_helper import get_libs_dict
from app.helpers.db_helper import db_retrieve_avail_libs_dict, db_update_avail_libs_dict, db_retrieve_last_updated, db_retrieve_book_records, db_update_book_records
from app.helpers.book_records_helper import book_records_by_classification

from functools import wraps
from operator import itemgetter
from humanize import naturaltime
from datetime import datetime
from gevent import monkey
monkey.patch_all()

## TODO LIST
## Deal with possible update failure in route '/update'
## (Optimization) Don't want to keep retrieving from db if book_record = [] or avail_libs_dict = {}?
## (Optimization) Delete Record for user with no availability records (?)


#### WRAPPERS

def identifier_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            if session['identifier']:
                return f(*args, **kwargs)
        except:
            return redirect('/login')
    return decorated_function


#### ROUTES

@app.route('/login', methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        session['identifier'] = login_form.identifier.data
        session['avail_libs_dict'] = {}
        session['last_updated'] = None
        session['book_records'] = []
        return redirect('/')
    return render_template('login.html', login_form=login_form)

@app.route('/')
@identifier_required
def index():
    try:
        avail_libs_dict = session['avail_libs_dict'] or \
                          db_retrieve_avail_libs_dict(session['identifier'])
        last_updated = session['last_updated'] or \
                       db_retrieve_last_updated(session['identifier'])
        time_diff_str = naturaltime(datetime.utcnow() - last_updated)
        return render_template('index.html',
                               avail_libs_dict=avail_libs_dict,
                               time_diff_str=time_diff_str)
    except:
        return render_template('index.html')

@app.route('/update')
@identifier_required
def update():
    book_records = session['book_records']
    avail_libs_dict = get_libs_dict(book_records)
    db_update_avail_libs_dict(avail_libs_dict, session['identifier'])
    session['avail_libs_dict'] = avail_libs_dict
    session['last_updated'] = db_retrieve_last_updated(session['identifier'])
    return redirect('/')

@app.route('/view', methods=['GET','POST'])
@identifier_required
def view():
    add_form = AddForm()
    delete_form = DeleteForm()

    if add_form.validate_on_submit(): # Valid AddForm request
        book_records = session['book_records']
        book_record = {}
        book_record['brn'] = add_form.brn.data
        book_record['title'] = add_form.title.data
        book_record['author'] = add_form.author.data
        book_record['classification'] = add_form.classification.data
        book_records.append(book_record)
        book_records = sorted(book_records, key=itemgetter('classification', 'title'))
        session['book_records'] = book_records
        db_update_book_records(book_records, session['identifier'])
        return redirect('/view')

    if delete_form.validate_on_submit(): #Valid DeleteForm request
        if not 1 <= delete_form.number.data <= len(session['book_records']):
            return redirect('/view')
        book_records = session['book_records']
        book_records.pop(delete_form.number.data - 1)
        session['book_records'] = book_records
        db_update_book_records(book_records, session['identifier'])
        return redirect('/view')

    book_records = session['book_records'] or \
                   sorted(db_retrieve_book_records(session['identifier']),
                          key=itemgetter('classification', 'title'))
    session['book_records'] = book_records
    split_book_records = book_records_by_classification(book_records)

    return render_template('view.html',
                           add_form=add_form,
                           delete_form=delete_form,
                           split_book_records=split_book_records)
