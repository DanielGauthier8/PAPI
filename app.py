import datetime
import os
import secrets
import time

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from flask import Flask, render_template, flash, request, redirect, url_for, session
from werkzeug.utils import secure_filename

import db_actions

UPLOAD_FOLDER = 'databases'
ALLOWED_EXTENSIONS = {'db'}

app = Flask(__name__)

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH=300 * 1024 * 1024,
    SECRET_KEY='zdfxfghjkbhgfdhvgc',
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(minutes=15)
)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    session.permanent = True
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


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

            return redirect(url_for('results', token=token))
    return render_template('upload_file.html')


@app.route('/upload_file_many', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        # check if the post request has the file part
        uploaded_files = request.files.getlist('file[]')
        # print(uploaded_files)
        files_list = []
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename, file_extension = os.path.splitext(secure_filename(file.filename))
                # print(filename)
                token = secrets.token_urlsafe(16)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], token))
                files_list.append([(os.path.join(app.config['UPLOAD_FOLDER'], token)), filename])
        session[token] = files_list
        print(files_list)
        return redirect(url_for('filter', token=token))
    return render_template('upload_file_many.html')

@app.route('/student_files/<token>', methods=['GET', 'POST'])
def results(token):
    cursor, conn = db_actions.set_cursor(os.path.join(app.config['UPLOAD_FOLDER'], token))
    cursor = db_actions.clean_up(cursor, False, False)

    file_bounds = db_actions.documentBounds(cursor)

    if token not in session:
        session[token] = None
    session[token] = db_actions.all_files(cursor)

    if request.method == 'POST':
        temp = request.form.getlist('chosen_files')
        if "All Files" not in str(temp):
            session[token] = temp
        if request.form['start'] is not "na":
            cursor = db_actions.clean_up(cursor, request.form['start'], request.form['end'])

            # db_actions.chopDocument(os.path.join(app.config['UPLOAD_FOLDER'], token), request.form['start'], request.form['end'], True)

        return redirect(url_for('file_analysis', token=token) + "?start=" + request.form['start'] + "&end=" + request.form['end'])
    return render_template('student_info.html', files_list=session[token], file_bounds=file_bounds)


@app.route('/filter/<token>', methods=['GET', 'POST'])
def filter(token):
    
    if request.method == 'POST':
        return redirect(url_for('file_analysis_many', token=token) + "?start=" + request.form['start'] + "&end=" + request.form['end'])
    else:
        bounds = []
        for file in session[token]:
            print(file)
            cursor, conn = db_actions.set_cursor(file[0])
            cursor = db_actions.clean_up(cursor, False, False)

            print(db_actions.documentBounds(cursor))
            [start, end] = db_actions.documentBounds(cursor)
            bounds.append(start)
            bounds.append(end)

        return render_template('date-select.html', file_bounds=bounds, token=token)


@app.route('/file_analysis/<token>', methods=['GET', 'POST'])
def file_analysis(token):
    # milliseconds = int(round(time.time() * 1000))
    if not session[token]:
        return redirect(url_for('results', token=token))
    db_actions.clear_old_files()
    file_dat, graphs, the_timeline, deletion_insertion_timeline = db_actions. \
        all_data(os.path.join(app.config['UPLOAD_FOLDER'], token), session[token], request.args.get('start'), request.args.get('end'))
    user_selection, the_timeline, graphs = db_actions.time_graph_granularity(the_timeline, graphs, "hour", True)

    if request.method == 'POST':
        file_dat, graphs, the_timeline, deletion_insertion_timeline = db_actions. \
            all_data(os.path.join(app.config['UPLOAD_FOLDER'], token), session[token], request.args.get('start'), request.args.get('end'))

        user_selection, the_timeline, graphs = db_actions.time_graph_granularity(the_timeline, graphs,
                                                                                 request.form['granularity'],
                                                                                 True)

        return render_template('file_analysis.html', file_dat=file_dat, graphs=graphs, the_timeline=the_timeline,
                               deletion_insertion_timeline=deletion_insertion_timeline, user_selection=user_selection)
    # print(int(round(time.time() * 1000)) - milliseconds)
    return render_template('file_analysis.html', file_dat=file_dat, graphs=graphs, the_timeline=the_timeline,
                           deletion_insertion_timeline=deletion_insertion_timeline, user_selection=user_selection)


@app.route('/file_analysis_many/<token>', methods=['GET', 'POST'])
def file_analysis_many(token):

    db_actions.clear_old_files()
    zip_path = db_actions.download_generation(session[token], canvas, letter, request.args.get('start'), request.args.get('end'))
    graphs, the_timeline, deletion_insertion_timeline, heatmaps, file_dat = db_actions. \
        multiple_database_get_data(session[token], request.args.get('start'), request.args.get('end'))
    user_selection, the_timeline, graphs = db_actions.time_graph_granularity(the_timeline, graphs, "hour", True)
    if request.method == 'POST':

        graphs, the_timeline, deletion_insertion_timeline, heatmaps, file_dat = db_actions. \
            multiple_database_get_data(session[token], request.args.get('start'), request.args.get('end'))

        user_selection, the_timeline, graphs = db_actions.time_graph_granularity(the_timeline, graphs,
                                                                                 request.form['granularity'],
                                                                                 True)

        return render_template('file_analysis_many.html', graphs=graphs, the_timeline=the_timeline,
                               deletion_insertion_timeline=deletion_insertion_timeline,
                               heatmaps=heatmaps, file_dat=file_dat, user_selection=user_selection, zip_path=zip_path)

    return render_template('file_analysis_many.html', graphs=graphs, the_timeline=the_timeline,
                           deletion_insertion_timeline=deletion_insertion_timeline,
                           heatmaps=heatmaps, file_dat=file_dat, user_selection=user_selection, zip_path=zip_path)

