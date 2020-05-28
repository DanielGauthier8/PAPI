import sqlite3
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

print("Running")


# ----------------------------------------Helper Functions
def remove_char_from_string(the_string, the_characters):
    for the_char in the_characters:
        the_string = the_string.replace(the_char, "")
    return the_string


# ----------------------------------------Database Management


def db_string_to_array(the_string):
    """Cleans db strings of leftover byte characters

    Parameters
    ----------
    the_string : str
        The string to be cleaned

    Returns
    -------
    the_string
        A cleaned string
    """
    the_string = remove_char_from_string(str(the_string), ['b', '[', ']', "'", '\"'])

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


def set_cursor(filename):
    """Provides a cursor of the sqlite db

    Parameters
    ----------
    filename : str
        The filename of the db to be browsed

    Returns
    -------
    cursor
        A cursor to browse the sql db from the file provided
    """
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    return cursor


def clean_up(cursor):
    """Removes private/undesired data from provided db

    Parameters
    ----------
    cursor : cursor
        The current db cursor object

    Returns
    -------
    cursor
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
    cursor : cursor
        The current db cursor object
    db_name : string
        The name of the database
    column : string
        The db column name
    like_string: string
        The string to look for in a column
    Returns
    -------
    cursor
        Cursor object matching column values
    """
    cursor.execute("SELECT * FROM " + db_name + " WHERE " + column + " LIKE '%" + like_string + "%'")
    return cursor


# Save points added, to return the array of save points
document_dict = {"id": 0, "file_path": 1, "file_contents": 2, "file_hash": 3,
                 "auth_attributes": 4, "save_points": 5, "revision_number": 6, "created_at": 7,
                 "updated_at": 8, "last_update": 9, "new_line_char": 10, "saves": 15}


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
        fetch
            String of metadata
        """
    cursor = get_like_db(cursor, "Documents", "path", file_name)
    student_file = cursor.fetchone()
    index = document_dict[lookup_item]
    fetch = student_file[index % 10]
    if index % 10 == 5:
        fetch = db_string_to_array(fetch)
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
    fetch
        List of metadata
    """
    fetch = []
    i = 0
    for file_name in file_namez:
        # Gets specific document columns
        cursor = get_like_db(cursor, "Documents", "path", file_name)
        student_file = cursor.fetchone()
        index = document_dict[lookup_item]
        fetch.append(student_file[index % 10])
        if index % 10 == 5:
            fetch.append(db_string_to_array(fetch[i]))
        if index == 15:
            fetch.append(len(db_string_to_array(fetch[i])))
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
    general_pulse
        Dictionary of user insertions and deletions (filename::return time, inserted_text)
    """
    document_id = document_info(cursor, file_name, "id")
    general_pulse = {}
    current_timeline = []

    cursor.execute("SELECT operation, created_at FROM Revisions WHERE document_id = " + str(document_id))
    operation_array = cursor.fetchall()

    for text in operation_array:
        block_insertions = "i"
        block_deletions = "d"
        operation_str_arr = db_string_to_array(text)
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
            while file_name + "::" + str(the_timestamp) in general_pulse:
                the_timestamp += datetime.timedelta(seconds=1)

            general_pulse[file_name + "::" + str(the_timestamp)] = \
                [str(block_insertions).replace("\\\\n", "").replace("////", ""),
                 block_deletions.replace("\\\\n", "").replace("////", "")]
            current_timeline.append(the_timestamp)
    # (filename::return time, inserted_text) -> dictionary
    return current_timeline, general_pulse


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
    general_pulse
        Dictionary of user insertions and deletions (filename::return time, inserted_text)
    """
    many_file_pulses = {}
    current_timeline = []
    for file_name in files:
        times_only, gathered = gather(cursor, file_name)
        many_file_pulses = {**many_file_pulses, **gathered}
        current_timeline += times_only

    return current_timeline, many_file_pulses


def all_pulses(general_pulse):
    """Finds programming events in dictionary by converting key value pairs into parsable actions

    Parameters
    ----------
    general_pulse : dictionary
        Dictionary of user insertions and deletions
    Returns
    -------
    data_pulse
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
    for element in general_pulse:
        comments_list.append(general_pulse[element].count("//") +
                             general_pulse[element].count("/*"))

        logic_list.append(general_pulse[element].count("if") +
                          general_pulse[element].count("elif") + general_pulse[element].count("else"))

        operation_list.append(general_pulse[element].count("=") + general_pulse[element].count("+=") +
                              general_pulse[element].count("-=") + general_pulse[element].count("*") +
                              general_pulse[element].count("*="))

        output_list.append(general_pulse[element].count("return") + general_pulse[element].count("cout"))
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
    all_the_files
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
    comment_num
        Number of comments
    """
    # Returns the number of comments in final file
    # comments, function, logic
    comments = []
    comment_num = 0
    # print(general_pulse)
    for element in documentz:
        element = str(element)
        comments.append(int(element.find("//")))
        comments.append(int(element.find("/*")))
        comments.append(int(element.find("# ")))
        comments.append(int(element.find("<!--")))

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
    general_pulse : dictionary
        Dictionary of user insertions and deletions
    Returns
    -------
    large_insertions
        Large insertions in dictionary with file information as key
    """
    large_insertions = {}
    average = 0
    for element in general_pulse:
        # print(general_pulse[element])

        average += len(general_pulse[element])

    try:
        average = average / len(general_pulse)
    except ZeroDivisionError:
        average = 0
    for element in general_pulse:
        insertion_size = len(remove_char_from_string(str(general_pulse[element]), [" ", "////"]))
        if (insertion_size > average * 8 and insertion_size > 40) or len(general_pulse[element]) > 400:
            large_insertions[element] = str(general_pulse[element]).replace("\n", "<br/>").replace("////", "")

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
    time_data_array
        Dictionary with name as key and value as data
    """
    sessions_list = []
    session = []
    number_of_days = 0
    average_session_length = 0
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
    return {"Time Worked": str(total_time), "Number of Work Sessions": len(sessions_list),
            "Over Number of Days": number_of_days, "Average Work Session Length": str(total_time / len(sessions_list))}


def deletions_insertions(the_pulse) -> (int, int):
    """Gets the number of deletions and insertions of filez

    Parameters
    ----------
    the_pulse : dict
        The current db cursor object
    Returns
    -------
    deletions
        The number of deletions of the filez provided
    insertions
        The number of insertions of the filez provided
    """
    deletions_list = []
    insertions_list = []
    # print(the_pulse)
    for operation in the_pulse:
        operation_string = the_pulse[operation]
        # print(operation_string)
        # if operation_string != "b'[]'":
        #     if operation_string.count('","d') > 0:
        #         deletions_list.append(1)
        #     else:
        #         deletions_list.append(0)
        #
        #     if operation_string.count('","i') > 0:
        #         insertions_list.append(1)
        #     else:
        #         insertions_list.append(0)

    deletions = sum(deletions_list)
    insertions = sum(insertions_list)
    return deletions, insertions, deletions_list, insertions_list


# ----------------------------------------Website Actions


def all_data(db_file, file_namez):
    """Calls all required helper functions to get all non-graphic metadata

    Parameters
    ----------
    db_file : string
        The current db file name
    file_namez : list
        Names of the files to look through
    Returns
    -------
    file_dat
        Dictionary of all metadata retrieved
    """
    # Returns all file metadata
    cursor = set_cursor(db_file)
    cursor = clean_up(cursor)

    file_dat = {}

    names = ""
    for name in file_namez:
        names = names + "  " + name
    file_dat["File Name(s)"] = names

    time_list, the_pulse = gather_many(cursor, file_namez)
    time_data = time_spent(time_list)
    file_dat = {**file_dat, **time_data}

    # Make sure sorted by date
    creation_datez = documentz_info(cursor, file_namez, "created_at")
    file_dat["First File Creation Date"] = creation_datez[0]
    file_dat["Last File Creation Date"] = creation_datez[len(creation_datez) - 1]
    # TODO: file_dat["Number of Saves"] = sum(documentz_info(cursor, file_namez, "saves"))
    edit_datez = documentz_info(cursor, file_namez, "updated_at")
    file_dat["Last Edit Date"] = edit_datez[len(edit_datez) - 1]

    deletions, insertions, deletions_list, insertions_list = deletions_insertions(the_pulse)
    file_dat["Number of Deletion Chuncks*"] = deletions
    file_dat["Number of Insertion Chuncks*"] = insertions

    file_dat["Number of Comments*"] = comment_count(documentz_info(cursor, file_namez, "file_contents"))

    file_dat["Large Text Insertion Detection*"] = large_insertion_check(the_pulse)

    return file_dat


# ----------------------------------------Debugging


def test():
    cursor = set_cursor("./databases/jgoldman2468.db")
    cursor = clean_up(cursor)
    files_list = all_files(cursor)
    # print(files_list)
    time_list, the_pulse = gather_many(cursor, files_list)
    deletions, insertions, deletions_list, insertions_list = deletions_insertions(the_pulse)

    print(len(deletions_list), len(insertions_list), len(time_list), len(the_pulse))
    # fig = plt.figure()
    # ax = plt.subplot(111)
    # ax.plot(time_list, deletions_list, label='Deletions Over Time')
    # plt.title('Legend inside')
    # ax.legend()
    # plt.show()
    # print(large_insertion_check(the_pulse))
    # doc_file = documentz_info(cursor, files_list, "save_points")
    # print(doc_file)
    # deletions, insertions = deletions_insertions(cursor, files_list)
    # print(str(deletions) + " " + str(insertions))

    # general_pulse = gather(cursor, the_file)
    # print(general_pulse)
    #
    # print(data_pulse)

    return 0


test()
