import sqlite3
import datetime
import time
import os
import zipfile

from reportlab.graphics import renderPDF
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.lib import colors
from reportlab.lib.colors import purple, blue, red, gray, green, black
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.pagesizes import letter

print("Running")


def clear_old_files():
    databases = os.listdir("./databases")
    # print(databases)
    for i, file, in enumerate(databases):
        if datetime.datetime.strptime(time.ctime(os.stat("./databases/" + file).st_atime), "%a %b %d %H:%M:%S %Y") + datetime.timedelta(days= 10) < datetime.datetime.now():
            # File is older than 10 days, delete to save hard drive space
            os.remove("./databases/" + file)


clear_old_files()
# Auto-delete older files at server startup

# ----------------------------------------Helper Functions


def graph_out(the_timeline, graphs):
    """Shows basic use of a line chart."""
    data = []
    the_max = 0
    for graph in graphs:
        if max(graph) > the_max:
            the_max = max(graph)
        new_list = [(i, graph[i]) for i in range(0, len(the_timeline))]  # str(the_timeline[i])
        data.append(new_list)
    drawing = Drawing(500, 300)
    lp = LinePlot()
    lp.height = 300
    width, height = letter
    lp.width = width - 80
    lp.data = data
    # lp.lineLabelFormat = '%2.0f'
    lp.strokeColor = colors.black
    # comments, logic, operations, output
    lp.lines[0].strokeColor = colors.green
    lp.lines[0].symbol = makeMarker('FilledCircle')
    lp.lines[1].strokeColor = colors.blue
    lp.lines[1].symbol = makeMarker('FilledCircle')
    lp.lines[2].strokeColor = colors.purple
    lp.lines[2].symbol = makeMarker('FilledCircle')
    lp.lines[3].strokeColor = colors.red
    lp.lines[3].symbol = makeMarker('FilledCircle')
    # lp.xValueAxis.valueMin = 0
    # lp.xValueAxis.valueMax = 5
    # lp.xValueAxis.valueStep = 1
    lp.yValueAxis.valueMin = 0
    lp.yValueAxis.valueMax = the_max + 30
    # lp.yValueAxis.valueStep = 1
    drawing.add(lp)
    return drawing


def make_legend (the_canvas):
    start_y = 300
    the_canvas.setFillColor(gray)
    the_canvas.rect(150, 230, 300, 80, fill=True, stroke=True)
    the_canvas.setFillColor(green)
    the_canvas.rect(180, 270, 20, 15, fill=True, stroke=True)
    the_canvas.setFillColor(black)
    the_canvas.drawString(160, start_y, "Comments")
    the_canvas.setFillColor(blue)
    the_canvas.rect(250, 270, 20, 15, fill=True, stroke=True)
    the_canvas.setFillColor(black)
    the_canvas.drawString(240, start_y, "Logic")
    the_canvas.setFillColor(purple)
    the_canvas.rect(320, 270, 20, 15, fill=True, stroke=True)
    the_canvas.setFillColor(black)
    the_canvas.drawString(295, start_y, "Operations")
    the_canvas.setFillColor(red)
    the_canvas.rect(390, 270, 20, 15, fill=True, stroke=True)
    the_canvas.setFillColor(black)
    the_canvas.drawString(380, start_y, "Output")


def heading(true_filename, the_canvas, the_letter):
    width, height = the_letter
    the_canvas.setFont('Courier', 14)
    the_canvas.drawString(30, 750, 'PAPI Student Feedback')
    the_canvas.drawString(30, 735, 'University of Rhode Island')
    the_canvas.drawString(370, 750, "Date Generated: " + str(datetime.date.today()))
    the_canvas.setFont('Courier', 12)
    the_canvas.drawString(30, 683, 'Name:')
    the_canvas.line(0, 680, width, 680)
    the_canvas.drawString(120, 683, true_filename)


def __remove_char_from_string(the_string, the_characters):
    for the_char in the_characters:
        the_string = the_string.replace(the_char, "")
    return the_string


def __db_string_to_array(the_string):
    """Cleans db strings of leftover byte characters

    Parameters
    ----------
    the_string : str
        The string to be cleaned

    Returns
    -------
    the_string : str
        A cleaned string
    """
    the_string = __remove_char_from_string(str(the_string), ['b', '[', ']', "'", '\"'])

    the_string = the_string.split(',')
    test_list = []
    # Empty list
    if len(the_string) == 1 and (the_string[0] == '' or the_string[0] == '[]'):
        the_string = []

    try:
        test_list = [int(i) for i in the_string]
    except TypeError:
        return the_string
    except ValueError:
        return the_string

    return test_list


def __cumulative_list(the_list):
    new_list = []
    current_sum = 0
    for i in the_list:
        current_sum += i
        new_list.append(current_sum)
    return new_list


def time_graph_granularity(time_list, items_list, zoom_level, skip_no_activity=True):
    """Change the granularity of a user actions over time

    Parameters
    ----------
    time_list : list
        List of times in chronological order
    items_list : list
        The list to pair down
    zoom_level : string
        The interval size between events
    skip_no_activity : bool
        Chooses if the blank activity times are shown or hidden

    Returns
    -------
    new_time_list : list
        New shorter times list in chronological order
    new_item_list : list
        New list of user actions on less granular timeline
    user_selection: dict
        Provides checking and unchecking information for user form
    """

    # Zoom levels
    zoom_options = {"day": datetime.timedelta(days=1), "hour": datetime.timedelta(hours=1),
                    "minute": datetime.timedelta(minutes=1)}
    # default, all unchecked
    user_selection = {"day": "", "hour": "", "minute": "",
                      "skip_no_activity": "", "show_no_activity": ""}
    new_time_list = []
    new_item_list = []

    if skip_no_activity:
        user_selection["skip_no_activity"] = "checked"
    else:
        user_selection["show_no_activity"] = "checked"

    user_selection[zoom_level] = "checked"

    current_max_time = None
    for count in items_list:
        # start and array of each
        new_item_list.append([0])
    index = 0
    last_value = None
    if skip_no_activity:
        for the_time in time_list:
            if current_max_time is None:
                current_max_time = the_time + zoom_options[zoom_level]

            if current_max_time > the_time:
                for list_index in range(0, len(items_list)):
                    new_item_list[list_index][len(new_item_list[list_index])-1] += items_list[list_index][index]
            else:
                if zoom_level == "day":
                    new_time_list.append(current_max_time.date())
                elif zoom_level == "hour":
                    new_time_list.append(current_max_time.strftime("%Y-%m-%d, %H")+":00")
                else:
                    new_time_list.append(current_max_time.strftime("%Y-%m-%d, %H:%M"))

                for count in range(0, len(items_list)):
                    # start and array of each
                    new_item_list[count].append(0)
                current_max_time = the_time + zoom_options[zoom_level]

            index += 1

    return user_selection, new_time_list, new_item_list


def zip_dir(path, filename):
    # Adapted from https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python
    zip_file = zipfile.ZipFile(filename + '.zip', 'w', zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(path):
        for file in files:
            zip_file.write(os.path.join(root, file), arcname=file)

    zip_file.close()
# ----------------------------------------Database Management


def set_cursor(filename):
    """Provides a cursor of the sqlite db

    Parameters
    ----------
    filename : str
        The filename of the db to be browsed

    Returns
    -------
    cursor : object
        A cursor to browse the sql db from the file provided
    """
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    return cursor


def clean_up(cursor):
    """Removes private/undesired data from provided db

    Parameters
    ----------
    cursor : object
        The current db cursor object

    Returns
    -------
    cursor : object
        Database with unnecessary data removed
    """
    # Remove all hidden file histories
    cursor.execute("DELETE FROM Documents WHERE path LIKE \'.%\'")
    # STEP 3: "DROP TABLE ChatMessages"
    cursor.execute('DROP TABLE IF EXISTS ChatMessages')
    # STEP 4: "DROP TABLE Environments"
    cursor.execute('DROP TABLE IF EXISTS Environments')
    return cursor


def get_like_db(cursor, db_name, column, like_string):
    """Gets any db row with specific column value

    Parameters
    ----------
    cursor : object
        The current db cursor object
    db_name : string
        The name of the database
    column : string
        The db column name
    like_string: string
        The string to look for in a column
    Returns
    -------
    cursor: object
        Cursor object matching column values
    """
    cursor.execute("SELECT * FROM " + db_name + " WHERE " + column + " LIKE " + ' "%' + like_string + '%"')
    return cursor


# ----------------------------------------Data Collection


def document_info(cursor, file_name, lookup_item):
    """Gets any specific file metadata from a final resulting file

        Parameters
        ----------
        cursor : cursor
            The current db cursor object
        file_name : string
            The filename of the file to lookup
        lookup_item : string
            The name of the metadata to be accessed, have to be in document_dict list
        Returns
        -------
        fetch : str
            String of metadata
        """

    # Save points added, to return the array of save points
    document_dict = {"id": 0, "file_path": 1, "file_contents": 2, "file_hash": 3,
                     "auth_attributes": 4, "save_points": 5, "revision_number": 6, "created_at": 7,
                     "updated_at": 8, "last_update": 9, "new_line_char": 10, "saves": 15}

    cursor = get_like_db(cursor, "Documents", "path", file_name)
    student_file = cursor.fetchone()
    index = document_dict[lookup_item]
    fetch = student_file[index % 10]
    if index % 10 == 5:
        fetch = __db_string_to_array(fetch)
    if index == 15:
        fetch = len(fetch)

    return fetch


def documentz_info(cursor, file_namez, lookup_item):
    """Gets any specific file metadata from a list of final resulting filez

    Parameters
    ----------
    cursor : cursor
        The current db cursor object
    file_namez : list
        List of files to look through
    lookup_item : string
        The name of the metadata to be accessed, have to be in document_dict list
    Returns
    -------
    fetch : list
        List of metadata
    """
    document_dict = {"id": 0, "file_path": 1, "file_contents": 2, "file_hash": 3,
                     "auth_attributes": 4, "save_points": 5, "revision_number": 6, "created_at": 7,
                     "updated_at": 8, "last_update": 9, "new_line_char": 10, "saves": 15}
    fetch = []
    i = 0
    for file_name in file_namez:
        # Gets specific document columns
        cursor = get_like_db(cursor, "Documents", "path", file_name)
        student_file = cursor.fetchone()
        index = document_dict[lookup_item]
        fetch.append(student_file[index % 10])
        if index % 10 == 5:
            fetch.append(__db_string_to_array(fetch[i]))
        if index == 15:
            fetch.append(len(__db_string_to_array(fetch[i])))
        i += 1

    return fetch


def gather(cursor, file_name):
    """Converts SQLite db into an easier to manage dictionary

    Parameters
    ----------
    cursor : cursor
        The current db cursor object
    file_name : string
        Name of the file to create dictionary of
    Returns
    -------
    general_pulse :dict
        Dictionary of user insertions and deletions (filename::return time, inserted_text)
    """
    document_id = document_info(cursor, file_name, "id")
    general_pulse = {}

    cursor.execute("SELECT operation, created_at FROM Revisions WHERE document_id = " + str(document_id))
    operation_array = cursor.fetchall()

    for text in operation_array:
        block_insertions = "i"
        block_deletions = "d"
        operation_str_arr = __db_string_to_array(text)
        # print(operation_str_arr)
        if len(operation_str_arr) > 2:
            for element in operation_str_arr:

                # Only insertions and deletions, ignoring space only actions
                if len(element) - element.count(' ') > 1 and (element[:1] == "i" or element[:1] == "d"):

                    if element[:1] == "i":
                        block_insertions += str(element[1:])
                    if element[:1] == "d":
                        block_deletions += str(element[1:])
            the_timestamp = datetime.datetime.strptime(text[len(text) - 1], '%Y-%m-%d %H:%M:%S')
            while the_timestamp in general_pulse:
                the_timestamp += datetime.timedelta(seconds=1)

            general_pulse[the_timestamp] = \
                [__remove_char_from_string(str(block_insertions), ("\\\\n", "\\\\n", "////", " \\ ", "\\t"))
                    , __remove_char_from_string(str(block_deletions), ("\\\\n", "\\\\n", "////", " \\ ", "\\t")),
                                                file_name]
    # (filename::return time, inserted_text) -> dictionary
    return general_pulse


def gather_many(cursor, files):
    """Converts SQLite db into an easier to manage dictionary

    Parameters
    ----------
    cursor : cursor
        The current db cursor object
    files : list
        Names of the files to create dictionary of
    Returns
    -------
    general_pulse : dict
        Dictionary of user insertions and deletions (filename::return time, inserted_text)
    """
    many_file_pulses = {}
    for file_name in files:
        gathered = gather(cursor, file_name)
        many_file_pulses = {**many_file_pulses, **gathered}

    # many_file_pulses = sorted(many_file_pulses)
    the_timeline = list(many_file_pulses.keys())
    the_timeline.sort()
    return the_timeline, many_file_pulses


def all_pulses(the_timeline, the_pulse):
    """Finds programming events in dictionary by converting key value pairs into parsable actions

    Parameters
    ----------
    the_pulse : dict
        The current db of user actions in a datetime keyed dictionary
    the_timeline : list
        sorted by date, timeline of the_pulse keys
    Returns
    -------
    data_pulse : dict
        New parsable dictionary
    """
    # TODO All pulses
    # comments, function, logic
    data_pulse = []
    # comments, logic, operations, return
    comments_list = []
    logic_list = []
    operation_list = []
    output_list = []
    for element in the_timeline:
        comments_list.append(the_pulse[element][0].count("// ") +
                             the_pulse[element][0].count("/*"))

        logic_list.append(the_pulse[element][0].count("if") +
                          the_pulse[element][0].count("elif") + the_pulse[element][0].count("else"))

        operation_list.append(the_pulse[element][0].count("=") + the_pulse[element][0].count("+=") +
                              the_pulse[element][0].count("-=") + the_pulse[element][0].count("*") +
                              the_pulse[element][0].count("*="))

        output_list.append(the_pulse[element][0].count("return") + the_pulse[element][0].count("cout"))

    data_pulse = [comments_list, logic_list, operation_list, output_list]

    return data_pulse


def all_files(cursor):
    """Finds all filenames in db

    Parameters
    ----------
    cursor : cursor
        The current db cursor object action_times
    Returns
    -------
    all_the_files : list
        List of filenames
    """
    all_the_files = []
    # Create folder for user
    cursor.execute('SELECT * FROM Users LIMIT 1')
    user_info = cursor.fetchone()
    # print(user_info[0])

    cursor.execute("SELECT * FROM Documents")
    student_file = cursor.fetchone()
    # First create all the files
    while student_file is not None:
        all_the_files.append(student_file[1])
        student_file = cursor.fetchone()
    return all_the_files


# ----------------------------------------Data Generation


def comment_count(documentz):
    """Gets the number of comments in file in its current state

    Parameters
    ----------
    documentz : list
        List of documents to count comments in
    Returns
    -------
    comment_num : int
        Number of comments
    """
    # Returns the number of comments in final file
    # comments, function, logic
    comments = []
    comment_num = 0
    # print(documentz)
    for element in documentz:

        element = str(element)
        comments.append(int(element.count("// ")))
        comments.append(int(element.count("/*")))
        comments.append(int(element.count("# ")))
        comments.append(int(element.count("<!--")))

    for i in comments:
        if i > 0:
            comment_num += i

    return comment_num


def large_insertion_check(general_pulse):
    """Finds the average insertion size of the user,
    if there are elements with a greater than 800% difference
    between the regular insertion size the element is flagged

    Parameters
    ----------
    general_pulse : dict
        Dictionary of user insertions and deletions
    Returns
    -------
    large_insertions
        Large insertions in dictionary with file information as key
    """
    large_insertions = {}
    average = 0
    for element in general_pulse:
        # print(general_pulse[element][0][1:])

        average += len(general_pulse[element][0][1:])

    try:
        average = average / len(general_pulse)
    except ZeroDivisionError:
        average = 0
    for element in general_pulse:
        insertion_size = len(__remove_char_from_string(str(general_pulse[element][0][1:]), [" ", "///"]))
        if (insertion_size > average * 8 and insertion_size > 40) or len(general_pulse[element]) > 400:
            large_insertions[general_pulse[element][2]] = str(general_pulse[element][0][1:]).\
                replace("\n","<br/>").replace("////", "").replace("\\", "")

    if len(large_insertions) > 0:
        return large_insertions

    return -1


def time_spent(timeline_list):
    """Calculates the time spent on each set of files provided

    Parameters
    ----------
    timeline_list : list
        List of datetime, each a user action
    Returns
    -------
    time_data_list : list
        Dictionary with name as key and value as data
    """
    sessions_list = []
    session = []
    number_of_days = 0
    # If only one edit in a day
    if len(timeline_list) == 1:
        return {"Time Worked on Assigment": 5, "Number of Work Sessions": 1, "Over Number of Days": 1}

    try:
        previous = timeline_list[0]
    except IndexError:
        return 0

    timeline_list.sort()

    for user_action_time in timeline_list:
        if user_action_time.date() > previous.date():
            number_of_days += 1
        if user_action_time > previous + datetime.timedelta(minutes=5):
            sessions_list.append(session)
            session = []
        session.append(user_action_time)

        previous = user_action_time
    total_time = None
    current_time = 0
    for the_session in sessions_list:

        current_time = the_session[len(the_session) - 1] - the_session[0]
        if total_time is None:
            total_time = current_time
        total_time = total_time + current_time
    try:
        average_session_length = str(total_time / len(sessions_list))
    except TypeError:
        average_session_length = total_time

    return {"Time Worked": str(total_time), "Number of Work Sessions": len(sessions_list),
            "Over Number of Days": number_of_days, "Average Work Session Length": average_session_length}


def deletions_insertions(the_timeline, the_pulse) -> (int, int):
    """Gets the number of deletions and insertions of filez

    Parameters
    ----------
    the_pulse : dict
        The current db of user actions in a datetime keyed dictionary
    the_timeline : list
        sorted by date, timeline of the_pulse keys
    Returns
    -------
    deletions : int
        The number of deletions of the filez provided
    insertions : int
        The number of insertions of the filez provided
    deletions_list : list
        List in chronological order, marking number of deletions at each user action
    insertions_list : list
        List in chronological order, marking number of insertions at each user action

    """
    deletions = 0
    insertions = 0
    deletions_list = []
    insertions_list = []
    # print(the_pulse)
    for operation_string in the_timeline:
        # print(operation_string[0])
        # print(operation_string)
        if len(the_pulse[operation_string][0]) > 1:
            insertions += len(the_pulse[operation_string][0])
            insertions_list.append(the_pulse[operation_string][0])
        else:
            insertions_list.append(0)

        if len(the_pulse[operation_string][1]) > 1:
            deletions += len(the_pulse[operation_string][1])
            deletions_list.append(len(the_pulse[operation_string][1]))
        else:
            deletions_list.append(0)

    # print(insertions)

    return deletions, insertions, deletions_list, insertions_list


# ----------------------------------------Website Actions
def get_meta_data(the_cursor, the_timeline, the_pulse, file_namez):
    """Calls all required helper functions to get non-graphical metadata

    Parameters
    ----------
    the_pulse : dict
        The current db of user actions in a datetime keyed dictionary
    the_timeline : list
        sorted by date, timeline of the_pulse keys
    Returns
    -------
    meta_data_list
        list of all collected metadata from file list
    """
    local_file_data = {}
    creation_datez = documentz_info(the_cursor, file_namez, "created_at")
    local_file_data["First File Creation Date"] = creation_datez[0]
    local_file_data["Last File Creation Date"] = creation_datez[len(creation_datez) - 1]
    # TODO: file_dat["Number of Saves"] = sum(documentz_info(cursor, file_namez, "saves"))
    edit_datez = documentz_info(the_cursor, file_namez, "updated_at")
    local_file_data["Last Edit Date"] = edit_datez[len(edit_datez) - 1]

    deletions, insertions, deletions_list, insertions_list = deletions_insertions(the_timeline, the_pulse)
    local_file_data["Number of Deletion Characters"] = deletions
    local_file_data["Number of Insertion Characters"] = insertions

    local_file_data["Number of Comments*"] = comment_count(documentz_info(the_cursor, file_namez, "file_contents"))

    local_file_data["Large Text Insertion Detection*"] = large_insertion_check(the_pulse)
    return local_file_data, deletions_list, insertions_list


def build_file_history(pulse, buildingMultiStudentArray = False):
    # Builds a JSON string of the pulse history for client-side processing
    file_history = ""
    if not buildingMultiStudentArray:
        file_history = "["
    for i in pulse:
        if len(pulse[i][0]) > 1:
            file_history += "{\"time\": \"" + i.isoformat() + "\", "
            file_history += "\"o\": \"" + pulse[i][0][:1] + "\"},"
        if len(pulse[i][1]) > 1:
            file_history += "{\"time\": \"" + i.isoformat() + "\", "
            file_history += "\"o\": \"" + pulse[i][1][:1] + "\"},"
    if not buildingMultiStudentArray:
        file_history = file_history[:-1] + "]"
    return file_history


def all_data(db_file, file_namez):
    """Calls all required helper functions to get all metadata

    Parameters
    ----------
    db_file : string
        The current db file name
    file_namez : list
        Names of the files to look through
    Returns
    -------
    file_dat
        Dictionary of all basic metadata retrieved
    graphs
            List of lists of different programming actions
    the_timeline: list
        Chronolical list of all dates
    """
    # Returns all file metadata
    cursor = set_cursor(db_file)
    # cursor = clean_up(cursor)

    file_dat = {}

    names = ""
    for name in file_namez:
        names = names + "  " + name
    file_dat["File Name(s)"] = names

    the_timeline, the_pulse = gather_many(cursor, file_namez)
    time_data = time_spent(the_timeline)
    file_dat = {**file_dat, **time_data}
    meta_data, deletions_list, insertions_list = get_meta_data(cursor, the_timeline, the_pulse, file_namez)
    file_dat = {**file_dat, **meta_data}
    graphs = all_pulses(the_timeline, the_pulse)

    deletion_insertion_timeline = build_file_history(the_pulse)

    return file_dat, graphs, the_timeline, deletion_insertion_timeline


def multiple_database_get_data (db_filename_list):
    """Calls all required helper functions to get all metadata for class mode, multi-student analysis

        Parameters
        ----------
        db_filename_list : list
            Names of the database files to look through
        Returns
        -------
        graphs
            List of lists of different programming actions
        the_timeline: list
            Chronological list of all dates
        file_dat: dict
            Summary of metadata trends across student files
        deletion_insertion_timeline:

        """

    list_of_pulses = []
    deletion_insertion_timeline = {}
    overall_time_line = []
    heatmaps = "["

    for db_file, true_filename in db_filename_list:
        cursor = set_cursor(db_file)
        cursor = clean_up(cursor)
        the_timeline, the_pulse = gather_many(cursor, all_files(cursor))
        overall_time_line.extend(the_timeline)
        list_of_pulses.append(the_pulse)
        heatmaps += build_file_history(the_pulse, True)

    file_dat = time_spent(overall_time_line)

    heatmaps = heatmaps[:-1] + "]"

    many_student_pulse = list_of_pulses.pop(0)

    for student_db_file in list_of_pulses:
        for action in student_db_file:
            try:
                temp = many_student_pulse[action]
                many_student_pulse[action] = [temp[0] + student_db_file[action][0][:1], temp[1] + student_db_file[action][1][:1], temp[2] + "  " + student_db_file[action][2]]
            except KeyError:
                many_student_pulse[action] = student_db_file[action]

    the_timeline = list(many_student_pulse.keys())
    the_timeline.sort()
    graphs = all_pulses(the_timeline, many_student_pulse)

    return graphs, the_timeline, deletion_insertion_timeline, heatmaps, file_dat


def download_generation(db_filename_list, outter_canvas, letter):
    print(db_filename_list[len(db_filename_list) - 1][0])
    download_path = os.path.join("report_generation", os.path.basename(db_filename_list[len(db_filename_list) - 1][0]))
    try:
        os.mkdir(download_path)
    except FileExistsError:
        print("File already exists")

    for db_file, true_filename in db_filename_list:
        cursor = set_cursor(db_file)
        cursor = clean_up(cursor)
        file_namez = all_files(cursor)
        file_dat, graphs, the_timeline, deletion_insertion_timeline = all_data(db_file, file_namez)

        the_canvas = outter_canvas.Canvas(os.path.join(download_path, true_filename) + ".pdf", pagesize=letter)
        the_canvas.setLineWidth(.3)
        heading(true_filename, the_canvas, letter)
        start_y = 650
        gap = 350
        the_canvas.setFont('Courier-Bold', 12)
        the_canvas.drawString(30, start_y, "File Name(s)")
        the_canvas.setFont('Courier', 12)
        for files in file_namez:
            the_canvas.drawString(30 + gap, start_y, files)
            start_y -= 20
            if start_y < 40:
                the_canvas.showPage()
                heading(true_filename, the_canvas, letter)
                start_y = 650

        for key, value in file_dat.items():
            if len(str(value)) < 20:
                the_canvas.setFont('Courier-Bold', 12)
                the_canvas.drawString(30, start_y, str(key))
                the_canvas.setFont('Courier', 12)
                the_canvas.drawString(30 + gap, start_y, str(value))
                start_y -= 20
                the_canvas.drawString
            if key == "Large Text Insertion Detection*" and value == -1:
                the_canvas.setFont('Courier-Bold', 12)
                the_canvas.drawString(30, start_y, str(key))
                the_canvas.setFont('Courier', 12)
                the_canvas.drawString(30 + gap, start_y, "False")
                start_y -= 20
            if start_y < 40:
                the_canvas.showPage()
                heading(true_filename, the_canvas, letter)
                start_y = 650
        the_canvas.setFont('Courier-Bold', 12)
        the_canvas.drawString(30, start_y, "Large Text Insertion Detection*")
        start_y -= 20
        if file_dat["Large Text Insertion Detection*"] != -1:
            for one_instance_key, one_instance_value in file_dat["Large Text Insertion Detection*"].items():
                the_canvas.setFont('Courier-Bold', 12)
                the_canvas.drawString(30 + 10, start_y, one_instance_key)
                start_y -= 20
                split_values = one_instance_value.split("    ")
                for j in split_values:
                    chunk_size = 60
                    for one_line in range(0,len(j),60):
                        the_canvas.setFont('Courier', 12)
                        the_canvas.drawString(30 + 20, start_y, j[one_line:one_line+60])
                        start_y -= 20
                        if start_y < 40:
                            the_canvas.showPage()
                            heading(true_filename, the_canvas, letter)
                            start_y = 650
                start_y -= 20
                if start_y < 40:
                    the_canvas.showPage()
                    heading(true_filename, the_canvas, letter)
                    start_y = 650

        user_selection, the_timeline, graphs = time_graph_granularity(the_timeline, graphs,
                                                                                 'day')
        drawing = graph_out(the_timeline, graphs)
        the_canvas.setFont('Courier-Bold', 14)
        start_y -= 20
        the_canvas.showPage()
        width, height = letter
        heading(true_filename, the_canvas, letter)
        the_canvas.drawString((width / 2) - 50, 650, "ACTIVITY BY TYPE")
        renderPDF.draw(drawing, the_canvas, 30, 320, showBoundary=False)
        make_legend(the_canvas)

        the_canvas.save()
    zip_path = os.path.join("static", "zipped_exports", os.path.basename(db_filename_list[len(db_filename_list) - 1][0]))
    zip_dir(download_path, zip_path)

    return os.path.join("..", (zip_path + ".zip"))
