from prettytable import PrettyTable
from collections import defaultdict
import unittest
import os
import sqlite3


class University:

    def __init__(self, dir):

        self.student_container = dict()
        self.insturctor_container = dict()
        self.majors = dict()       
        self.all_majors = dict() 
        self.student_reader(os.path.join(dir, 'students.txt'))
        self.insturctor_reader(os.path.join(dir, 'instructors.txt'))
        self.grade_reader(os.path.join(dir, 'grades.txt'))
        self.majors_reader(os.path.join(dir, 'majors.txt'))
        self.student_table()
        self.insturctor_table()
        self.majors_table()
    
    def read_file(self, path, fields, sep = ',', header = False):
        'read text files and yeild value for that line'

        try:

            fl= open(path,"r")

        except FileNotFoundError:
            raise FileNotFoundError(f"Cannot open '{path}' file")

        else:
            with fl:

                line_num= 1
                lines = fl.readlines()

                for line in lines:
                    line= line.strip().split(sep)
                    line = tuple(line)
                    
                    field_num = len(line)

                    if field_num != fields:
                        raise ValueError('{}, has {} fields on line {} but expected {}'.format(fl.name,fields,line_num,field_num))

                    if not (line_num == 1 and header == True):
                        yield line

                    line_num +=1

    
    def student_reader(self,path):

        for CWID, Name, Major in self.read_file(path, 3, '\t', False):
            self.student_container[CWID] = Student(CWID, Name, Major)

    def insturctor_reader(self, path):

        for CWID, Name, dept in self.read_file(path, 3, '\t', False):
            self.insturctor_container[CWID] = Instructor(CWID, Name, dept)

    def grade_reader(self, path):

        for CWID, courseName, std_grades, instrCWID in self.read_file(path, 4, '\t', False):
            
            self.student_container[CWID].add_grade(courseName, std_grades)
            self.insturctor_container[instrCWID].add_student(courseName)

    def majors_reader(self, path):

        for major, flag, course in self.read_file(path, 3 , '\t', False):

            if major not in self.majors:
                self.majors[major]= {'R': [], 'E': []}

            if flag == 'R':
                self.majors[major]['R'].append(course)
            elif flag == 'E':
                self.majors[major]['E'].append(course)

        for student in self.student_container.values():
            student.add_remainingCourses(self.majors)

        for m in self.majors:
            self.all_majors[m] = Major(m, self.majors[m]['R'], self.majors[m]['E'])
        
        return self.majors
    
    def student_table(self):

        pt_student = PrettyTable(field_names= Student.fields_name())

        for std in self.student_container.values():
            pt_student.add_row(std.details())
        
        print(pt_student)
    
    def insturctor_table(self):

        DB_path = "/Users/MaramAlrshoud/Documents/Universites/Stevens/Spring2019/SSW-810A/homeworks/hw11/810_startup.db"
        db = sqlite3.connect(DB_path)

        query = """SELECT i.CWID, i.Name, i.Dept, g.Course, count(g.Course) as students from instructors i
                   JOIN grades g ON i.CWID = g.Instructor_CWID group by g.Course order by students desc"""

        pt_inst = PrettyTable(field_names= Instructor.fields_name())

        for row in db.execute(query):

            pt_inst.add_row(row)

        print(pt_inst)


    def majors_table(self):

        pt_major = PrettyTable(field_names= Major.fields_name())

        for major in self.all_majors.values():
            pt_major.add_row(major.details())
        
        print(pt_major)

class Student:
    
    def __init__(self, CWID, Name, Major):
        
        self.CWID = CWID
        self.Name = Name
        self.Major = Major
        self.classTaken = dict()
        self.remRequired = []
        self.remElectives = []

        
    def add_grade(self, courseName, std_grades):
        # key is course name and the  value is grade 

        self.classTaken[courseName]= std_grades

    def add_remainingCourses(self, majors):
        
 
        checkTaken = self.classTaken.copy()
        Elective_completed = []

        for course in checkTaken:

            if self.classTaken[course] in ['F', 'D', 'D-', 'D+']:

                del self.classTaken[course] 
        
        for major in majors.keys():

            remR = [value for value in majors[major]['R'] if value not in self.classTaken.keys() and self.Major == major]
            self.remRequired += remR

        for major in majors.keys():

            remE = [value for value in majors[major]['E'] if value not in self.classTaken.keys() and self.Major == major]

            Elective_completed += [value for value in majors[major]['E'] if value in self.classTaken.keys() and self.Major == major]
            self.remElectives += remE
        
        if len(Elective_completed) > 0:

            self.remElectives = []


    def details(self):
        #provide all fields of each std as a list for creating table/test

        return[self.CWID, self.Name, self.Major, sorted(self.classTaken.keys()), self.remRequired, self.remElectives]

    @staticmethod

    def fields_name():
        return['CWID', 'Name', 'Major', 'Completed Courses', ' Remaining requiared', 'Remaining Electives']

class Instructor:

    def __init__ (self, CWID, Name, dept):

        self.CWID = CWID
        self.Name = Name
        self.dept = dept
        self.taughtCourses = defaultdict(int)

    def add_student(self, course):
        
        self.taughtCourses[course] += 1  #key is the Name of the course and value is number of stds

    def ints_details(self):

        for key,value in self.taughtCourses.items():
            yield [self.CWID, self.Name, self.dept, key, value]

    @staticmethod

    def fields_name():
        return['CWID', 'Name', 'Dept', 'Course', 'Students']

class Major:

    def __init__(self, major, required, elective):
        
        self.requried = required
        self.elective = elective
        self.major = major

    def details (self):
        return [self.major, self.requried, self.elective]
    
    @staticmethod
    
    def fields_name():
        return ['Dept', 'Required', 'Elective']

def main():
    dir = "/Users/MaramAlrshoud/Documents/Universites/Stevens/Spring2019/SSW-810A/homeworks"
    print(University(dir))

main()

class testing(unittest.TestCase):

    def test_classes(self):

        DB_path = "/Users/MaramAlrshoud/Documents/Universites/Stevens/Spring2019/SSW-810A/homeworks/hw11/810_startup.db"
        db = sqlite3.connect(DB_path)

        query = """SELECT i.CWID, i.Name, i.Dept, g.Course, count(g.Course) as students from instructors i
                   JOIN grades g ON i.CWID = g.Instructor_CWID group by g.Course order by students desc"""

        dir="/Users/MaramAlrshoud/Documents/Universites/Stevens/Spring2019/SSW-810A/homeworks"

        t1= University(dir)
        self.maxDiff = None
        
        std_result = [['10103', 'Baldwin, C', 'SFEN', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687'], ['SSW 540','SSW 555'], []], 
                      ['10115', 'Wyatt, X', 'SFEN', ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687'], ['SSW 540', 'SSW 555'], []], 
                      ['10172', 'Forbes, I', 'SFEN', ['SSW 555', 'SSW 567'], ['SSW 540', 'SSW 564'], ['CS 501', 'CS 513', 'CS 545']], 
                      ['10175', 'Erickson, D', 'SFEN', ['SSW 564', 'SSW 567', 'SSW 687'],['SSW 540', 'SSW 555'], ['CS 501', 'CS 513', 'CS 545']], 
                      ['10183', 'Chapman, O', 'SFEN', ['SSW 689'], ['SSW 540', 'SSW 564', 'SSW 555', 'SSW 567'], ['CS 501', 'CS 513', 'CS 545']],
                      ['11399', 'Cordova, I', 'SYEN', ['SSW 540'], ['SYS 671', 'SYS 612', 'SYS 800'], []], 
                      ['11461', 'Wright, U', 'SYEN', ['SYS 611', 'SYS 750', 'SYS 800'], ['SYS 671', 'SYS 612'], ['SSW 810', 'SSW 540', 'SSW 565']], 
                      ['11658', 'Kelly, P', 'SYEN', [], ['SYS 671', 'SYS 612', 'SYS 800'], ['SSW 810', 'SSW 540', 'SSW 565']], 
                      ['11714', 'Morton, A', 'SYEN', ['SYS 611' , 'SYS 645'], ['SYS 671', 'SYS 612', 'SYS 800'], ['SSW 810', 'SSW 540', 'SSW 565']], 
                      ['11788', 'Fuller, E', 'SYEN', ['SSW 540'], ['SYS 671', 'SYS 612', 'SYS 800'], []]]

        instruct_result = [('98765', 'Einstein, A', 'SFEN', 'SSW 567', 4), 
                           ('98765', 'Einstein, A', 'SFEN', 'SSW 540', 3),
                           ('98764', 'Feynman, R', 'SFEN', 'SSW 564', 3),
                           ('98764', 'Feynman, R', 'SFEN', 'SSW 687', 3),
                           ('98760', 'Darwin, C', 'SYEN', 'SYS 611', 2),
                           ('98763', 'Newton, I', 'SFEN', 'SSW 555', 1),
                           ('98763', 'Newton, I', 'SFEN', 'SSW 689', 1), 
                           ('98760', 'Darwin, C', 'SYEN', 'SYS 645', 1),
                           ('98760', 'Darwin, C', 'SYEN', 'SYS 750', 1),
                           ('98760', 'Darwin, C', 'SYEN', 'SYS 800', 1)]
        
        major_result = [['SFEN', ['SSW 540', 'SSW 564', 'SSW 555', 'SSW 567'],['CS 501', 'CS 513', 'CS 545']],
                       ['SYEN', ['SYS 671', 'SYS 612', 'SYS 800'], ['SSW 810', 'SSW 540', 'SSW 565']]]



        listStudents = [student.details() for student in t1.student_container.values()]
        listInstructors = [row for row in db.execute(query)]
        ListMajors = [major.details() for major in t1.all_majors.values()]

        
        self.assertEqual(listStudents, std_result) 
        self.assertEqual(listInstructors, instruct_result)
        self.assertEqual(ListMajors, major_result)

if __name__ == '__main__':
    main()
    unittest.main(exit = False, verbosity = 2)
