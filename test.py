from datetime import date

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
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


def heading(canvas, letter):
    width, height = letter
    canvas.setFont('Courier', 14)
    canvas.drawString(30, 750, 'PAPI Student Feedback')
    canvas.drawString(30, 735, 'University of Rhode Island')
    canvas.drawString(370, 750, "Date Generated: " + str(date.today()))
    canvas.setFont('Courier', 12)
    canvas.drawString(30, 683, 'Name:')
    canvas.line(0, 680, width, 680)
    canvas.drawString(120, 683, "JOHN DOE")


def main(canvas):
    cursor = db_actions.set_cursor("./databases/7bT48DZyuHxGz0WGDJB-0A")
    cursor = db_actions.clean_up(cursor)
    file_namez = db_actions.all_files(cursor)
    file_dat, graphs, the_timeline, deletion_insertion_timeline = db_actions.all_data("./databases/7bT48DZyuHxGz0WGDJB-0A", file_namez)
    canvas = canvas.Canvas("form.pdf", pagesize=letter)
    canvas.setLineWidth(.3)
    heading(canvas, letter)
    start_y = 650
    start_x = 200
    gap = 350
    canvas.drawString(30, start_y, "File Name(s)")
    for files in file_namez:
        canvas.drawString(30 + gap, start_y, files)
        start_y -= 20
        if start_y < 40:
            canvas.showPage()
            heading(canvas,letter)
            start_y = 650

    for key, value in file_dat.items():
        if len(str(value)) < 20:
            canvas.drawString(30, start_y, str(key))
            canvas.drawString(30 + gap, start_y, str(value))
            start_y -= 20
            canvas.drawString
        if key == "Large Text Insertion Detection*" and value == -1:
            canvas.drawString(30, start_y, str(key))
            canvas.drawString(30 + gap, start_y, "False")
            start_y -= 20

    canvas.drawString(30, start_y, "Large Text Insertion Detection*")
    start_y -= 20
    for one_instance_key, one_instance_value in file_dat["Large Text Insertion Detection*"].items():
        canvas.drawString(30 + (gap/2), start_y, one_instance_key)
        canvas.drawString(30 + (gap), start_y, one_instance_value)
        start_y -= 20
        if start_y < 40:
            canvas.showPage()
            heading(canvas,letter)
            start_y = 650

    canvas.save()

    return 0


main(canvas)
