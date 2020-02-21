import sqlite3
import os

print("Running")


def create_folders(cursor):
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
            if version is '' or version is (len(saved_star_rev)-1) or version is (len(saved_star_rev)-2):
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
    return str(the_string).strip('[]b').strip("'").replace('\"', '').split(',')


def get_cursor(filename):
    # STEP 1: Open file
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    return cursor


def clean_up(cursor):
    # STEP 2: "DELETE FROM Documents WHERE path LIKE '.%' ;
    # Remove all hidden file histories
    cursor.execute("DELETE FROM Documents WHERE path LIKE \'.%\'")
    # STEP 3: "DROP TABLE ChatMessages"
    cursor.execute('DROP TABLE IF EXISTS ChatMessages')
    # STEP 4: "DROP TABLE Environments"
    cursor.execute('DROP TABLE IF EXISTS Environments')
    return cursor


def get_like_db(cursor, db_name, column, like_string):
    cursor.execute("SELECT * FROM " + db_name + " WHERE " + column +
                   " LIKE '%" + like_string + "%'")
    return cursor


document_dict = {"id": 0, "file_path": 1, "file_contents": 2, "file_hash": 3,
                 "auth_attributes": 4, "saves": 5, "revision_number": 6, "created_at": 7,
                 "updated_at": 8, "last_update": 9, "new_line_char": 10}


def last_save(dirty_input):
    return len(db_string_to_array(dirty_input))


def document_info(cursor, file_name, lookup_item):
    cursor = get_like_db(cursor, "Documents", "path", file_name)
    student_file = cursor.fetchone()
    index = document_dict[lookup_item]
    fetch = student_file[index]
    if index == 5:
        fetch = last_save(fetch)

    return fetch


def deletions_insertions(cursor, file_name):
    document_id = document_info(cursor, file_name, "id")
    deletions = 0
    insertions = 0

    cursor.execute("SELECT operation FROM Revisions WHERE document_id = " + str(document_id))
    operation_array = cursor.fetchall()

    for operation in operation_array:
        operation_string = str(operation[0])
        # print(operation_string)
        deletions += operation_string.count(',"d')
        insertions += operation_string.count(',"i')
    return deletions, insertions


def gather(cursor, file_name):
    document_id = document_info(cursor, file_name, "id")

    general_pulse = {}

    cursor.execute("SELECT operation, created_at FROM Revisions WHERE document_id = " + str(document_id))
    operation_array = cursor.fetchall()

    for operation in operation_array:
        operation_str_arr = str(operation[0]).strip("b'").strip('[]').replace('\"', '').split(',')
        for element in operation_str_arr:
            if element[:1] == 'i':
                general_pulse[operation[1]] = element[1:]

    # return time: inserted text dictionary
    return general_pulse


def all_pulses(general_pulse):
    # comments, function, logic
    data_pulse = []

    for element in general_pulse:
        element_array = [element, general_pulse[element], general_pulse[element].count("//") +
                         general_pulse[element].count("/*")]
        data_pulse.append(element_array)

    return data_pulse


def main():
    the_cursor = get_cursor("./databases/92316106dd4e4f4baf314dd59dc4354f.db")
    the_file = "stack.h"
    cursor = clean_up(the_cursor)
    doc_file = document_info(cursor, the_file, "saves")

    deletions, insertions = deletions_insertions(cursor, the_file)
    print(str(deletions) + " " + str(insertions))

    general_pulse = gather(cursor, the_file)
    #print(general_pulse)
    data_pulse = all_pulses(general_pulse)

    print(data_pulse)


main()
