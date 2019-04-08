from prettytable import PrettyTable
from collections import defaultdict
import unittest
import os

class University:

    def __init__(self, dir):

        self.student_container = dict()
        self.insturctor_container = dict()        
        self.student_reader(os.path.join(dir, 'students.txt'))
        self.insturctor_reader(os.path.join(dir, 'instructors.txt'))
        self.grade_reader(os.path.join(dir, 'grades.txt'))
        self.student_table()
        self.insturctor_table()
    
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

    
    def student_table(self):

        pt_student = PrettyTable(field_names= Student.fields_name())
        for std in self.student_container.values():
            pt_student.add_row(std.details())
        
        print(pt_student)
    
    def insturctor_table(self):
        pt_inst = PrettyTable(field_names= ['CWID', 'Name', 'Dept', 'Course', 'Students'])

        for i in self.insturctor_container.values():
            for j in i.ints_details():
                pt_inst.add_row(j)

        print(pt_inst)


class Student:

    def __init__(self, CWID, Name, Major):

        self.CWID = CWID
        self.Name = Name
        self.Major = Major
        self.classTaken = dict()

    def add_grade(self, courseName, std_grades):
        # key is course name and the  value is grade 

        self.classTaken[courseName]= std_grades

    def details(self):
        #provide all fields of each std as a list for creating table/test

        return[self.CWID, self.Name, sorted(self.classTaken.keys())]

    @staticmethod
    def fields_name():
        return['CWID', 'Name', 'Completed Courses']

class Instructor:

    def __init__ (self, CWID, Name, dept):

        self.CWID = CWID
        self.Name = Name
        self.dept = dept
        self.taughtCourses = defaultdict(int)

    def add_student(self, course):

        #key is the Name of the course and value is number of stds
        self.taughtCourses[course] += 1

    def ints_details(self):
        for key,value in self.taughtCourses.items():
            yield [self.CWID, self.Name, self.dept, key, value]

    @staticmethod
    def fields_name():
        return['CWID', 'Name', 'Dept', 'Course', 'Students']


def main():
    dir = "/Users/MaramAlrshoud/Documents/Universites files/Stevens/Spring 2019/SSW-810A/homeworks"
    print(University(dir))

main()


class testing(unittest.TestCase):

    def test_classes(self):

        dir="/Users/MaramAlrshoud/Documents/Universites files/Stevens/Spring 2019/SSW-810A/homeworks"

        t1= University(dir)

        dicStudents = dict()
        dictInstructor = dict()
        self.maxDiff = None
        
        std_result = [['10103', 'Baldwin, C', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687']], 
                      ['10115', 'Wyatt, X', ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687']], 
                      ['10172', 'Forbes, I', ['SSW 555', 'SSW 567']], 
                      ['10175', 'Erickson, D', ['SSW 564', 'SSW 567', 'SSW 687']], 
                      ['10183', 'Chapman, O', ['SSW 689']], 
                      ['11399', 'Cordova, I', ['SSW 540']], 
                      ['11461', 'Wright, U', ['SYS 611', 'SYS 750', 'SYS 800']], 
                      ['11658', 'Kelly, P', ['SSW 540']], 
                      ['11714', 'Morton, A', ['SYS 611', 'SYS 645']], 
                      ['11788', 'Fuller, E', ['SSW 540']]]

        instruct_result = [['98765', 'Einstein, A', 'SFEN', 'SSW 567', 4], 
                           ['98765', 'Einstein, A', 'SFEN', 'SSW 540', 3],
                           ['98764', 'Feynman, R', 'SFEN', 'SSW 564', 3],
                           ['98764', 'Feynman, R', 'SFEN', 'SSW 687', 3],
                           ['98764', 'Feynman, R', 'SFEN', 'CS 501', 1],  
                           ['98764', 'Feynman, R', 'SFEN', 'CS 545', 1], 
                           ['98763', 'Newton, I', 'SFEN', 'SSW 555', 1],
                           ['98763', 'Newton, I', 'SFEN', 'SSW 689', 1], 
                           ['98760', 'Darwin, C', 'SYEN', 'SYS 800', 1],
                           ['98760', 'Darwin, C', 'SYEN', 'SYS 750', 1],
                           ['98760', 'Darwin, C', 'SYEN', 'SYS 611', 2],
                           ['98760', 'Darwin, C', 'SYEN', 'SYS 645', 1]]


        listStudents = [student.details() for student in t1.student_container.values()]
        listInstructors = [detail for instructor in t1.insturctor_container.values() for detail in instructor.ints_details()]
        
        self.assertEqual(listStudents, std_result) 
        self.assertEqual(listInstructors, instruct_result)

     

if __name__ == '__main__':
    main()
    unittest.main(exit = False, verbosity = 2)
