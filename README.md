
#Automated Detailed Programming Assignment Feedback
 
 
 
######Daniel Gauthier
######University of Rhode Island

#####Master of Science in Computer Science Thesis Proposal

 
###1.1	Statement of the Problem
Automatically graded assignments in the computer science classroom are becoming increasingly common at all stages of the learning process. Currently, feedback given by auto-grading software provides a grade, but does not give specific feedback on the nuances of programming. To better learn the skill of programming through personalized feedback, more detail needs to be supplied to the teacher for proper observation; for a student to become a master of their skill faster and to provide a more enjoyable programming experience, a teacher needs more information from the integrated development environment to properly assess and assist the student.
###1.2	Justification for and Significance of the Study
With a growing number of students going into the computer science field, course instructors are turning to auto-graders to more efficiently grade course assignments [1]. This allows less time to be put into grading and more time into teaching. Gradescope, a commonly used auto-grader, has adverts saying things such as, “Grade All Coursework in Half the Time” [5], and other companies such as Autogradr advertise the abundance of others already using their software [4]. At the University of Rhode Island, I have personally experienced two of my undergraduate courses grading all homework assignments using the aforementioned Gradescope. Other classes I have taken have since switched as well. Assignments would receive a grade of 100/100 if correct, and then full points deducted for any portion incorrectly running. The grade is based off of the final submitted file, but cannot indicate to an instructor the process the student used to make the end product. Improving the learning experience would mean the additional feedback will be provided, while not adding new inconveniences for the student or teacher. This feedback would include the analysis of the programming process and not just the submitted file. If the lecturer could provide automated feedback, the student’s quality of education is likely to improve [2]. This is based on my source, which states that more feedback leads to a better learning experience by creating an environment for faster improvement in coding skills [10].

Advanced forms of assignment feedback research has begun at other Universities. Carnegie Mellon University [9] has done research using grammars and abstract syntax trees to give student feedback on assignments. This research was presented in 2013 at the “First Workshop on AI-supported Education for Computer Science” in Memphis, Tennessee. Additional progress has not since been made by this group, and there still remains not a usable programming technique feedback product available. By focusing on giving the students and their teachers more detailed feedback about a students’ programming process, research can continue to progress in advanced automated assignment feedback.

I see this study as a sensible progression between my undergraduate research, and where I want to take my career after graduate school. All of my undergraduate research was completed in computer science education. I wrote course curricula, found lessons, and created materials. I also wrote assignments and quizzes. Upon completion of  my graduate degree I plan to enter the private sector in software engineering. I see this project as a perfect bridge between the two, successfully merging my interests in computer science education and software engineering.

This project will focus on a small sample of students, but its final product can be implemented on a large scale. The study and collection of data will be limited to University of Rhode Island students, but the software can be used at any institution. The end-product software can be used from the range of primary school to life long learners. The software will be written to run on current Linux and Unix based computers. The additional grading feedback will gather information on the quality of the code and how the assignment was coded. With this goal, the study will focus on applying this software in an educational setting, but it is also applicable elsewhere. This could include professional software engineers, companies looking to hire workers, and possibly other forms of written word. With the fast pace of computer science, everyone must continue learning throughout their career, giving this study a large variety of uses.
 
In the scope of education, the results from this study will be utilized by professors and lecturers to see how a student is progressing with their code writing. The proposed software will provide feedback to these experienced teachers, as the time they can allocate per student is limited. New teachers should also be considered consumers of this software to be created. Both novice and skilled teachers could use this software to their advantage. When speaking with the professors who proceeded to teach the courses I helped create, the grading work was typically reported as the most overwhelming aspect of teaching a new course. Grading requires a great deal of time and attention. You must know both what is right, and why something is wrong. This software could help buffer the gap for new teachers. The goal is to provide students with the support they need by making an instructor aware of who needs more guidance, when looking at the grades is not enough.

###1.3	Methodology
This research will instrument an IDE to provide summative and formative feedback on the student's approach to programming. A commonly used integrated development environment (IDE) implemented by the University of Rhode Island is the “cs50ide.” This software was chosen because it can run across operating systems, as well as over the internet via the cloud. Cs50ide creates a database that stores all keystroke history typed into the program. It saves this data on a per-document level, allowing the programmer to look back at previous versions of their document [6]. This is similar to version control found in Microsoft Word and Google Docs. The data can be analyzed to determine the procedure of which a programmer created their software. Students in the determined study population will be new to programming and will have different programming techniques and skill levels. While some students may have received computer science experience before this class, others may be learning the programming language for the first time. 

The study will be done completely online. Data will be collected after each assignment submission deadline for the class and will be analyzed and interpreted. Examples of data to be collected would be things such as save frequency and keystroke strings. This means data will be collected either weekly or biweekly. This data could be collected once, at the end of the semester, but this route will not be taken in order to minimize data loss. The study cannot depend on the reliability of a student’s computer.

To retrieve the database file from a student’s computer, the programming account files can be accessed after the student initially shares their account with a grader [7]. At the beginning of the semester, each student will share their account with the graders’ account, and the file can be fetched throughout the semester. This download will occur the day after any assignment is due in class. The data being collected will be assumed to be the student’s own work. If the code is not the students work, and is deemed to be an instance of plagiarism, the software should also be able to notify that. This data collection is dependent on the cs50ide correctly and consistently recording students’ typing progress. This software is highly reliable, and has a contact email if issues arise.

This study will be grouped into two sections, starting with collecting the initial student data, followed by analyzing which factors lead to higher grades on an assignment. With this data, the patterns of keystrokes will be analyzed. Different saved versions of the file could also be reconstructed. This data will contain metadata such as the number of times a file was saved, when each of these saves occurred, speed of text input, and last time saved. Data will allow insight into the programming process. Looking at which assignments score better grades will allow code to be graded from another perspective. The greater depth of detail of a student’s assignment will provide the teaching staff information at a level previously not attainable without sitting down and meeting with each student. While an assignment may run correctly, the student may have programmed it with the same technique as a different student that received poor grades on other assignments.

The data collected will be interpreted to discover what programming techniques lead to higher grades. The study has many questions to be answered as there are many ways a person can write code. Perhaps the students that succeed start each program with pseudocode before actually writing the full program. Maybe the best technique is to create a framework for all functions and then write their interior. Perhaps the student performs best when writing a program top to bottom, saving rarely, and does the assignment in one sitting. These are the questions the study will try to answer. The chunks of keystrokes will indicate the speed the student has typed and the order things were written in, giving away their programming technique. These strings of text will be inspected using statistics to compare the code process with the assignment grade. Some metrics to be used would be start time of assignment in relation to due date, the length of programming sessions, the number of programming sessions, and the order code elements are written. By finding similarities between programming styles of equally graded assignments, patterns will arise.

Assuming different programming techniques do lead to higher assignment grades, the study will shift to creating software that can take this same data and predict how well future students will do in the class. This software should be used to red-flag students early, between assignments, so that more aid and attention is brought to them before they may realize they need it. By recommending a student to attend office hours or take more time to review materials, the teacher can take action on perceived underperforming students. This will be done because there are many differences between correct code, and good code. A student’s program may give the output an autograder is looking for, but the code might have been written using largely copy and pasted code or not properly commented. It will be assumed that data accumulated over a semester will be able to indicate these findings.

A student that codes well over an entire semester is assumed to have nicely syntaxed code, written with a well thought out method. A student with a lower average on the corresponding assignments over a semester is assumed to have poor programming technique. This software will take the aggregate data to make predictions and numerically grade based on how the software will be written.
###1.4	Resources Required
For this research to be completed successfully, the student database is required to collect adequate data on different student programming techniques. This depends on the cs50ide software to be used as the IDE for the students, as well as requiring this software to continue to monitor and record document progress. Matching these files with the assignment’s overall grade will be used to identify stronger programmers from weaker ones. A computer with enough processing power will also be required. This should not be an issue, as all data operations can be processed on a personal computer. While this is not required, some minimal conversation between myself and the cs50ide help desk may also be needed. This software has already been announced to be used in specific classes during the Spring 2020 University of Rhode Island semester.













###1.5	Literature Cited
Heinrich, A. (2018). Careers in Computer Science: 5 Facts on this Flourishing Field You Can No Longer Ignore — Rasmussen College. [online] Rasmussen.edu. Available at: https://www.rasmussen.edu/degrees/technology/blog/careers-in-computer- science-face-the-facts/.
 
McKenzie, L. (2018). Autograder issues upset students at Berkeley. [online] Insid- ehighered.com. Available at: https://www.insidehighered.com/news/2018/11/30/autograder- issues-upset-students-berkeley.
 
Inroads.acm.org. (2018). ACM Inroads: Archive. [online] Available at: https://inroads.acm.org/
 
AutoGradr. (2019). Automatically grade programming assignments. [online] Available at: https://autogradr.com/.
 
Gradescope.com. (2019). Gradescope — Save time grading. [online] Available at: https://www.gradescope.com/.

Cs50.readthedocs.io. (2019). CS50 IDE — CS50 Docs. [online] Available at: https://cs50.readthedocs.io/ide/online/ [Accessed 28 Dec. 2019].

Lloyd, D. (2016). CS50 AP Newsletter — August 2016. [online] Medium. Available at: https://medium.com/@cs50/cs50-ap-newsletter-august-2016-6b84ee38d4c5.

Head, A., Glassman, E. and Soares, G. (2017). Proceedings of the Fourth (2017) ACM Conference on Learning Scale. New York, NY: ACM.
 
Rivers, K. and Koedinger, K. (2019). Automatic Generation of Programming Feedback: A Data-Driven Approach. [online] Publications.informatik.hu-berlin.de. Available at: https://publications.informatik.hu-berlin.de/archive/cses/publications/aied2013wsvolume9
 
U.S. Office of Personnel Management. (2019). Feedback is Critical to Improving Perfor- mance. [online] Available at: https://www.opm.gov/policy-data-oversight/performance- management/performance-management-cycle/monitoring/feedback-is-critical-to-improving- performance/ [Accessed 11 Dec. 2019].
 
Digitalcommons.odu.edu. (2019). [online] Available at: https://digitalcommons.odu.edu/cgi/viewcontent.cgi?a
