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

QUEUEID = 1

app = Flask(__name__)
app.config.from_object(__name__)

def execute_query(query, params = []):
    con = mdb.connect(SQL_SERVER, USERNAME, PASSWORD, DATABASE)
    cur = con.cursor()
    cur.execute(query, params)
    return cur.fetchall()
    

@app.route('/')
def index():
    try:
        if not session['waiting']:
            return render_template('addTicket.html')
    except KeyError:
        return render_template('addTicket.html')
    return render_template('queue.html')

@app.route('/add', methods=['POST'])
def add():
    print "here"
    student = request.form['name']
    queueLocation = get_queue_location(QUEUEID)
    description = request.form['description']
    status = 'waiting'
    query = "insert into tickets (queueID, queueLocation, description, status, \
studentID) values (%s, %s, %s, %s, %s)"
    execute_query(query, [QUEUEID, queueLocation, description,
                          status, student])
    session['waiting'] = True
    return render_template('queue.html')


def get_queue_location(queueID):
    query = "select ticketID from tickets where queueID = %s"
    rows = execute_query(query, [queueID])
    return len(rows)

def get_tickets():
    query = "select * from tickets where queueID = %s"
    return execute_query(query, [QUEUEID])
