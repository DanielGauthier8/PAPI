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
    return str(the_string).strip('[]').strip("'").replace('\"', '').split(',')


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


def get_document(cursor, file_name):
    cursor.execute("SELECT * FROM Documents WHERE path LIKE '%" + file_name + "%'")
    return cursor


def save_count(cursor, file_name):
    cursor = get_document(cursor, file_name)
    student_file = cursor.fetchone()
    return len(db_string_to_array(student_file)) - 1


def main():
    the_cursor = get_cursor("./databases/92316106dd4e4f4baf314dd59dc4354f.db")
    cursor = clean_up(the_cursor)
    num_saves = save_count(cursor, "/bash")
    print(num_saves)


main()
