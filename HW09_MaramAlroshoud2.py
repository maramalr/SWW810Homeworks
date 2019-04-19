import sqlite3
from flask import Flask, render_template

app= Flask(__name__)

@app.route('/instructors')

def instructors_summary():

        DB_path = "/Users/MaramAlrshoud/Documents/Universites/Stevens/Spring2019/SSW-810A/homeworks/hw11/810_startup.db"
        db = sqlite3.connect(DB_path)

        query = """SELECT i.CWID, i.Name, i.Dept, g.Course, count(g.Student_CWID) as students from instructors i
                   JOIN grades g ON i.CWID = g.Instructor_CWID
                   group by g.Course order by students desc"""

        rows = db.execute(query)

        # convert the query result into a list of dict to pass the template
        data = [{'cwid': cwid, 'name': name, 'Department': Dept, 'Course': Course, 'Students': Students}
                for cwid, name, Dept, Course, Students in rows]

        db.close()

        return render_template ('instructors_table.html',
                               title='Stevens Repository',
                               table_title="Number of students by course and instructor",
                               instructors=data)

app.run(debug=True)


