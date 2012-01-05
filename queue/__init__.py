from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import MySQLdb as mdb
import sys, traceback

#configuration
DEBUG = True
SECRET_KEY = 'development_key'
DATABASE = 'tgarv+helpQueue'
SQL_SERVER = 'sql.mit.edu'
USERNAME = 'tgarv'
PASSWORD = 'lam63sot'

QUEUE_ID = 1

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    try:
        if not session['logged_in']:
            return render_template('login.html')
        else:
            if not waiting_for_ticket():
                return render_template('newTicket.html', tickets=get_tickets(),
                                       name=session['name'],
                                       studentID=session['studentID'],
                                       queue=get_queue_title(),
                                       teachers=get_teachers())
            else:
                print str(session)
                return render_template('queue.html', tickets=get_tickets(),
                                       name=session['name'],
                                       studentID=session['studentID'],
                                       queue=get_queue_title(),
                                       teachers=get_teachers())
    ##Exception caught if session['logged_in'] not defined
    except KeyError as e:
        print "Error: ", e
        traceback.print_exc(file=sys.stdout)
        return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    name = request.form['name']
    location = request.form['location']
    print session
    return do_login(name, location)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return do_logout()

@app.route('/adminLogout', methods=['GET', 'POST'])
def adminLogout():
    return do_admin_logout()

@app.route('/addTicket', methods=['GET','POST'])
def addTicket():
    student = session['studentID']
    queueLocation = get_queue_location(QUEUE_ID)
    description = request.form['description']
    status = 'waiting'
    query = "insert into tickets (queueID, queueLocation, description, status, \
studentID) values (%s, %s, %s, %s, %s)"
    execute_query(query, [QUEUE_ID, queueLocation, description,
                          status, student])
    session['waiting'] = True
    return redirect(url_for('index'))
##    return render_template('queue.html', tickets=get_tickets(),
##                           name=session['name'], studentID=session['studentID'])

@app.route('/removeTicket', methods=['POST'])
def removeTicket():
    ticketID = request.form['ticketID']
    return do_remove_ticket(ticketID)

@app.route('/admin')
def admin():
    try:
        if not session['admin_logged_in']:
            return render_template('adminLogin.html')
        else:
            if not helping_ticket():
                return render_template('adminQueue.html', tickets=get_tickets(),
                                       queue=get_queue_title(), name=session['name'])
            else:
                return render_template('adminTicket.html', tickets=get_tickets(),
                                       queue=get_queue_title(), name=session['name'])
    ##Exception caught if session['admin_logged_in'] not defined
    except KeyError as e:
        print "Error: ", e
        traceback.print_exc(file=sys.stdout)
        return render_template('adminLogin.html')

@app.route('/adminLogin', methods=['POST'])
def adminLogin():
    name = request.form['name']
    password = request.form['password']
    location = request.form['location']
    return do_admin_login(name, password, location)

def execute_query(query, params = []):
    con = mdb.connect(SQL_SERVER, USERNAME, PASSWORD, DATABASE)
    cur = con.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    con.commit()
    return rows

def get_queue_title():
    query = "select description from queues where queueID=%s"
    rows = execute_query(query, [QUEUE_ID])
    return rows[0][0]

def execute_query_insert(query, table, params = []):
    con = mdb.connect(SQL_SERVER, USERNAME, PASSWORD, DATABASE)
    cur = con.cursor()
    cur.execute(query, params)
    con.commit()
    query = "select last_insert_id() from " + str(table)
    cur.execute(query)
    ID = cur.fetchone()[0]
    return ID

def get_queue_location(queueID):
    query = "select max(queueLocation) from tickets where queueID = %s"
    rows = execute_query(query, [queueID])
    location = rows[0][0]
    if location!=None:
        return location + 1
    return 0

def get_tickets():
    query = "select * from tickets where queueID = %s"
    rows = execute_query(query, [QUEUE_ID])
    return [dict(ticketID=row[0], studentID=row[5],
                 name=get_student_name_from_id(row[5]),
                 description=row[3]) for row in rows]
    

def waiting_for_ticket():
    query = "select * from tickets where queueID=%s and studentID=%s"
    rows = execute_query(query, [QUEUE_ID, session['studentID']])
    if len(rows) > 0:
        session['waiting'] = True
    else:
        session['waiting'] = False
    return session['waiting']

def do_login(name, location):
    query = "insert into students (queueID, name, location) values (%s, %s, %s)"
    studentID = execute_query_insert(query, "students", [QUEUE_ID, name, location])
    session['name'] = name
    session['studentID'] = studentID
    session['logged_in'] = True
    session['waiting'] = False
    return redirect(url_for('index'))

def do_logout():
    query = "delete from students where studentID=%s"
    execute_query(query, [session['studentID']])
    session['logged_in'] = False
    session['name'] = None
    session['studentID'] = None
    session['waiting'] = False
    return redirect(url_for('index'))

def do_remove_ticket(ticketID):
    query = "delete from tickets where ticketID=%s"
    execute_query(query, [ticketID])
    session['waiting'] = False
    return "Ticket Deleted"

def get_student_name_from_id(studentID):
    query = "select name from students where studentID=%s"
    row = execute_query(query, [studentID])
    try:
        return row[0][0]
    except IndexError:
        return "Null"

def do_admin_login(name, password, location):
    query = "select password from queues where queueID=%s"
    rows = execute_query(query, [QUEUE_ID])
    correct_password = rows[0][0]
    if correct_password != password:
        return "Incorrect password"
    query = "insert into teachers (queueID, name, location) values \
(%s, %s, %s)"
    adminID = execute_query_insert(query, "teachers", [QUEUE_ID, name, location])
    session['adminID'] = adminID
    session['admin_logged_in'] = True
    session['name'] = name
    session['helping_ticket'] = False
    return redirect(url_for('admin'))

def do_admin_logout():
    query = "delete from teachers where teacherID=%s"
    execute_query(query, [session['adminID']])
    session['admin_logged_in'] = False
    session['name'] = None
    session['adminID'] = None
    session['helping_ticket'] = False
    return redirect(url_for('admin'))

def helping_ticket():
    return session['helping_ticket']

def get_teachers():
    query = "select * from teachers where queueID=%s"
    rows = execute_query(query, [QUEUE_ID])
    return [dict(name=row[2], location=row[3], helping=row[4]) for row in rows]
