import db_actions


def test():
    cursor = db_actions.set_cursor("./databases/jgoldman2468.db")
    cursor = db_actions.clean_up(cursor)
    files_list = db_actions.all_files(cursor)
    # print(files_list)

    the_timeline, the_pulse = db_actions.gather_many(cursor, files_list)

    all_pulse_list = db_actions.all_pulses(the_timeline, the_pulse)
    #
    # print(all_pulse_list)
    # print(the_pulse)
    new_timeline, new_list = db_actions.time_graph_granularity(the_timeline, all_pulse_list, "day")

    # print(len(all_pulse_list), len(new_list), len(new_timeline))

    # print(large_insertion_check(the_pulse))
    # doc_file = documentz_info(cursor, files_list, "save_points")
    # print(doc_file)
    deletions, insertions, deletions_list, insertions_list = db_actions.deletions_insertions(the_timeline, the_pulse)
    print(str(deletions) + " " + str(insertions), deletions_list, insertions_list)


    #
    # print(data_pulse)

    return 0


test()
