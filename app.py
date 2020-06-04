import time
import os
import secrets

from flask import Flask, render_template, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename

import db_actions


UPLOAD_FOLDER = './databases'
ALLOWED_EXTENSIONS = {'db'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './databases'
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
app.config['SECRET_KEY'] = 'zdfxfghjkbhgfdhvgc'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start')
def start():
    return render_template('start.html')


@app.route('/learn_more')
def learn_more():
    return render_template('learn_more.html')


@app.route('/loading/<token>')
def loading(token):
    return render_template('loading.html', token=token)


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if "file_name" not in session:
            session['file_name'] = None
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # print(file)
            token = secrets.token_urlsafe(16)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], token))
            session['file_name'] = token

            return redirect(url_for('loading', token=token))
    return render_template('upload_file.html')


@app.route('/upload_files', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # if "file_name" not in session:
        #     session['file_name'] = None
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # print(file)
            token = secrets.token_urlsafe(16)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], token))
            # session['file_name'] = token

            return redirect(url_for('loading', token=token))
    return render_template('upload_file.html')


@app.route('/student_files/<token>', methods=['GET', 'POST'])
def results(token):
    time.sleep(2)
    cursor = db_actions.set_cursor(os.path.join(app.config['UPLOAD_FOLDER'], token))
    cursor = db_actions.clean_up(cursor)

    if token not in session:
        session[token] = None
    session[token] = db_actions.all_files(cursor)

    if request.method == 'POST':
        temp = request.form.getlist('chosen_files')
        if "All Files" not in str(temp):
            session[token] = temp
        return redirect(url_for('file_analysis', token=token))
    return render_template('student_info.html', files_list=session[token])


@app.route('/file_analysis/<token>')
def file_analysis(token):
    file_dat, graphs, the_timeline, deletion_insertion_timeline = db_actions.all_data(os.path.join(app.config['UPLOAD_FOLDER'], token),
                                                         session[token])
    return render_template('file_analysis.html', file_dat=file_dat, graphs=graphs, the_timeline=the_timeline,
                           deletion_insertion_timeline= deletion_insertion_timeline)
