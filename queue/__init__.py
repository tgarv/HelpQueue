from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import MySQLdb as mdb

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
                return render_template('addTicket.html', tickets=get_tickets())
            else:
                print str(session)
                return render_template('queue.html', tickets=get_tickets())
    ##Exception caught if session['logged_in'] not defined
    except KeyError:
        return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
    name = request.form['name']
    location = request.form['location']
    return do_login(name, location)

@app.route('/addTicket', methods=['POST'])
def addTicket():
    print "here"
    student = request.form['name']
    queueLocation = get_queue_location(QUEUE_ID)
    description = request.form['description']
    status = 'waiting'
    query = "insert into tickets (queueID, queueLocation, description, status, \
studentID) values (%s, %s, %s, %s, %s)"
    execute_query(query, [QUEUE_ID, queueLocation, description,
                          status, student])
    session['waiting'] = True
    return render_template('queue.html')

@app.route('/admin')
def admin():
    return render_template('admin.html', tickets=get_tickets())

def execute_query(query, params = []):
    con = mdb.connect(SQL_SERVER, USERNAME, PASSWORD, DATABASE)
    cur = con.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    con.commit()
    return rows

def execute_query_insert(query, table, params = []):
    con = mdb.connect(SQL_SERVER, USERNAME, PASSWORD, DATABASE)
    cur = con.cursor()
    cur.execute(query, params)
    con.commit()
    foo = "select last_insert_id() from " + str(table)
    print foo
    cur.execute(foo)
    ID = cur.fetchone()[0]
    return ID

def get_queue_location(queueID):
    query = "select ticketID from tickets where queueID = %s"
    rows = execute_query(query, [queueID])
    return len(rows)

def get_tickets():
    query = "select * from tickets where queueID = %s"
    return execute_query(query, [QUEUE_ID])

def waiting_for_ticket():
    return False

def do_login(name, location):
    query = "insert into students (queueID, name, location) values (%s, %s, %s)"
    studentID = execute_query_insert(query, "students", [QUEUE_ID, name, location])
    session['name'] = name
    session['studentID'] = studentID
    session['logged_in'] = True
    return redirect(url_for('index'))
