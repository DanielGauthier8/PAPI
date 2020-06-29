import os

import db_actions


def helper(file):
    cursor = db_actions.set_cursor("./mydir/" + file)
    print(file)
    cursor = db_actions.clean_up(cursor)
    files_list = db_actions.all_files(cursor)
    # print(files_list)

    the_timeline, the_pulse = db_actions.gather_many(cursor, files_list)
    num_comments = db_actions.comment_count(db_actions.documentz_info(cursor, files_list, "file_contents"))
    #
    # print(all_pulse_list)
    # print(the_pulse)

    # print(len(all_pulse_list), len(new_list), len(new_timeline))

    # print(large_insertion_check(the_pulse))
    # doc_file = documentz_info(cursor, files_list, "save_points")
    # print(doc_file)

    deletions, insertions, deletions_list, insertions_list = db_actions.deletions_insertions(the_timeline, the_pulse)

    print("del: " , str(deletions) , "insert: " , str(insertions) , "comments: " , num_comments)


def main():
    for file in os.listdir("./mydir"):
        helper(file)
        #
        # print(data_pulse)

    return 0


main()
