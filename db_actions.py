import os
import sqlite3

print("Running")


def create_folders(cursor):
    # No longer used, created a directory of all files created by student from db cursor provided
    # Create folder for user
    cursor.execute('SELECT * FROM Users LIMIT 1')
    user_info = cursor.fetchone()
    # print(user_info[0])

    # Create folder for new assignments
    if not os.path.exists(user_info[0]):
        os.makedirs(user_info[0])

    # Create a folder for each assignment
    cursor.execute("SELECT * FROM Documents")
    student_file = cursor.fetchone()
    # First create all the files
    while student_file is not None:
        # print(row)

        if not os.path.exists(user_info[0] + '/' + str(student_file[0])):
            os.makedirs(user_info[0] + '/' + str(student_file[0]))
        # The database saves the array in a unicode string
        saved_star_rev = db_string_to_array(student_file[5])
        # Get the file name, ignore the head of the path name
        head, tail = os.path.split(student_file[1])
        # print(string_to_array)
        for version in range(0, len(saved_star_rev)):
            # Create versions
            # Create file with correct name
            file = open(user_info[0] + '/' + str(student_file[0]) + '/' + saved_star_rev[version] + tail, "w+")
            # If there is only one version or its the last version
            if version is '' or version is (len(saved_star_rev) - 1) or version is (len(saved_star_rev) - 2):
                file.write(student_file[2])
            file.close()
        student_file = cursor.fetchone()

    # Then make all the edits to the files backwards
    cursor.execute("SELECT * FROM Documents WHERE revNum >= 2")

    student_file = cursor.fetchone()
    head, tail = os.path.split(student_file[1])

    # while student_file is not None:

    document_id_array = db_string_to_array(student_file[5])
    # Get a document with a revision history
    cursor.execute("SELECT * FROM Revisions WHERE document_id = " + str(student_file[0]) + " ORDER BY id DESC")
    student_file_rev_stars = db_string_to_array(student_file[5])

    previous_version_num = student_file_rev_stars[len(student_file_rev_stars) - 2]
    student_file_history = cursor.fetchone()
    print(student_file_history[6])
    while int(student_file_history[0]) > int(previous_version_num):
        the_operation = db_string_to_array(student_file_history[1])
        print(the_operation[1][1:])
        file = open(user_info[0] + '/' + str(student_file_history[6]) + '/' + previous_version_num + tail, "w+")
        student_file_history = cursor.fetchone()

    file.close()


def db_string_to_array(the_string):
    # Returns sting of byte text
    return str(the_string).strip('[]b').strip("'").replace('\"', '').split(',')


def set_cursor(filename):
    # Returns a cursor to browse the sql database from the file provided
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    return cursor


def clean_up(cursor):
    # Returns database with unnessesary data removed
    # Remove all hidden file histories
    cursor.execute("DELETE FROM Documents WHERE path LIKE \'.%\'")
    # STEP 3: "DROP TABLE ChatMessages"
    cursor.execute('DROP TABLE IF EXISTS ChatMessages')
    # STEP 4: "DROP TABLE Environments"
    cursor.execute('DROP TABLE IF EXISTS Environments')
    return cursor


def get_like_db(cursor, db_name, column, like_string):
    # Returns any db row with specfic collumn value
    cursor.execute("SELECT * FROM " + db_name + " WHERE " + column + " LIKE '%" + like_string + "%'")
    return cursor


# Save points added, to return the array of save points
document_dict = {"id": 0, "file_path": 1, "file_contents": 2, "file_hash": 3,
                 "auth_attributes": 4, "save_points": 5, "revision_number": 6, "created_at": 7,
                 "updated_at": 8, "last_update": 9, "new_line_char": 10, "saves": 15}


def documents_info(cursor, file_namez, lookup_item):
    # namez, can be singular or plural
    # Returns any metadata from documentz
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
            fetch.append(len(fetch[i]))
        i += 1

    return fetch


def document_info(cursor, file_name, lookup_item):
    # one document lookup
    # Returns any metadata from a single document
    # Gets specific document columns
    cursor = get_like_db(cursor, "Documents", "path", file_name)
    student_file = cursor.fetchone()
    index = document_dict[lookup_item]
    fetch = student_file[index % 10]
    if index % 10 == 5:
        fetch = db_string_to_array(fetch)
    if index == 15:
        fetch = len(fetch)

    return fetch


def deletions_insertions(cursor, file_names) -> (int, int):
    # Returns the number of deletions and insertions of filez
    deletions = 0
    insertions = 0
    for file_name in file_names:
        document_id = document_info(cursor, file_name, "id")
        cursor.execute("SELECT operation FROM Revisions WHERE document_id = " + str(document_id))
        operation_array = cursor.fetchall()

        for operation in operation_array:
            operation_string = str(operation[0])
            # print(operation_string)
            deletions += operation_string.count(',"d')
            insertions += operation_string.count(',"i')
    return deletions, insertions


def gather(cursor, file_name):
    # Convert SQLite database of one file to (timestamp:operation) dictionary
    document_id = document_info(cursor, file_name, "id")
    general_pulse = {}

    cursor.execute("SELECT operation, created_at FROM Revisions WHERE document_id = " + str(document_id))
    operation_array = cursor.fetchall()

    for text in operation_array:
        operation_str_arr = db_string_to_array(text[0])
        for element in operation_str_arr:
            if element[:1] == 'i' and len(element[1:]) > 0:
                general_pulse[file_name + "::" + text[1]] = str(element[1:]).replace("\\\\n", "").replace("////", "")

    # return time: inserted text :: dictionary
    return general_pulse


def gather_many(cursor, files):
    # Convert SQLite database of many files to a (timestamp:operation) dictionary
    many_file_pulses = {}
    for file_name in files:
        # print(file_name)
        gathered = gather(cursor, file_name)
        many_file_pulses = {**many_file_pulses, **gathered}

    # return - time: inserted text - > dictionary
    # print(many_file_pulses)
    return many_file_pulses


def all_pulses(general_pulse):
    # TODO All pulses
    # Finds programming events in the timestamp:operation dictionary
    # comments, function, logic
    data_pulse = []

    for element in general_pulse:
        element_array = [element, general_pulse[element], general_pulse[element].count("//") +
                         general_pulse[element].count("/*")]
        data_pulse.append(element_array)

    return data_pulse


def comment_count(documentz):
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


def all_files(cursor):

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


def large_insertion_check(general_pulse):
    # Finds the average insertion size of the user, if there are elements with a greater than 800% difference
    # between the regular insertion size the element is flagged
    large_insertions = {}
    average = 0
    for element in general_pulse:
        # print(general_pulse[element])
        average += len(general_pulse[element])

    average = average / len(general_pulse)
    for element in general_pulse:
        if (len(str(general_pulse[element]).replace("////", "").replace(" ", "")) > average * 8 and \
            len(general_pulse[element].replace("////", "").replace(" ", "")) > 40) \
                or len(general_pulse[element]) > 400:
            large_insertions[element] = str(general_pulse[element]).replace("\n", "<br/>").replace("////", "")

    if len(large_insertions) > 0:
        return large_insertions

    return -1


def all_data(db_file, file_namez):
    # Returns all file metadata
    cursor = set_cursor(db_file)
    cursor = clean_up(cursor)

    file_dat = {}

    names = ""
    for name in file_namez:
        names = names + "  " + name
    file_dat["File Name(s)"] = names

    file_dat["Time Spent on Assignment*"] = "1 Hour"

    # Make sure sorted by date
    creation_datez = documents_info(cursor, file_namez, "created_at")
    file_dat["First File Creation Date"] = creation_datez[0]
    file_dat["Last File Creation Date"] = creation_datez[len(creation_datez) - 1]

    edit_datez = documents_info(cursor, file_namez, "updated_at")
    file_dat["Last Edit Date"] = edit_datez[len(edit_datez) - 1]

    deletions, insertions = deletions_insertions(cursor, file_namez)
    file_dat["Number of Deletion Chuncks*"] = deletions
    file_dat["Number of Insertion Chuncks*"] = insertions
    the_pulse = gather_many(cursor, file_namez)
    file_dat["Number of Comments*"] = comment_count(documents_info(cursor, file_namez, "file_contents"))

    file_dat["Large Text Insertion Detection*"] = large_insertion_check(the_pulse)

    return file_dat


def test():
    cursor = set_cursor("./databases/34567654.db")
    cursor = clean_up(cursor)
    files_list = all_files(cursor)
    # print(files_list)
    the_pulse = gather_many(cursor, files_list)
    print(the_pulse)
    # print(large_insertion_check(the_pulse))
    # doc_file = documents_info(cursor, files_list, "created_at")
    # print(doc_file)
    # deletions, insertions = deletions_insertions(cursor, files_list)
    # print(str(deletions) + " " + str(insertions))

    # general_pulse = gather(cursor, the_file)
    # print(general_pulse)
    # data_pulse = all_pulses(general_pulse)
    #
    # print(data_pulse)

    return 0


test()
