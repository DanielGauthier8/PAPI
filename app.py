import time

from flask import Flask, render_template, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3
from db_actions import set_cursor, clean_up, all_files, all_data
import os

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


@app.route('/loading/<filename>')
def loading(filename):
    return render_template('loading.html')


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

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['file_name'] = UPLOAD_FOLDER + "/" + filename
            return redirect(url_for('loading', filename=filename))
    return render_template('upload_file.html')


@app.route('/student_files', methods=['GET', 'POST'])
def results():
    time.sleep(2)
    cursor = set_cursor(session['file_name'])
    cursor = clean_up(cursor)
    files_list = all_files(cursor)
    if "chosen_files" not in session:
        session['chosen_files'] = None
    if request.method == 'POST':
        # print(request.form.getlist('chosen_files'))
        session['chosen_files'] = request.form.getlist('chosen_files')
        return redirect(url_for('file_analysis'))
    return render_template('student_info.html', files_list=files_list)


@app.route('/file_analysis')
def file_analysis():
    file_dat = all_data(session['file_name'], session['chosen_files'])

    print(file_dat)

    return render_template('file_analysis.html', file_dat=file_dat)
