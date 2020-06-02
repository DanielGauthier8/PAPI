import db_actions


def test():
    cursor = db_actions.set_cursor("./databases/jgoldman2468.db")
    cursor = db_actions.clean_up(cursor)
    files_list = db_actions.all_files(cursor)
    # print(files_list)

    the_timeline, the_pulse = db_actions.gather_many(cursor, files_list)
    all_pulse_list = db_actions.all_pulses(the_timeline, the_pulse)

    print(len(all_pulse_list), len(the_timeline))
    # new_timeline, new_list = time_graph_granularity(the_timeline[0], all_pulse_list, "day")
    # print(len(all_pulse_list), len(new_list), len(new_timeline))

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
