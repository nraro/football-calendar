import os.path
from flask import render_template, request, redirect, url_for, Blueprint
import datetime
import sqlite3

CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT, day TEXT, interval TEXT)"
)

INSERT_USERS_RETURN_ID = "INSERT INTO users (name, day, interval) VALUES (?, ?, ?)"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, '..', "database.db")

print(db_path)
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

views = Blueprint('views', __name__)

today = datetime.date.today()
weekday = datetime.datetime.now().isocalendar()[2]
defaultWeekday = today - datetime.timedelta(days=weekday - 1)

success = ''

dates = []


@views.route('/api/users', methods=['POST'])
def create_users():
    global success, top3, dates, defaultWeekday, weekdays, today, weekday
    entryFound = False
    error = 'Ai selectat deja intervalele: '
    success = 'Te-ai inscris cu succes in perioada: '

    for n in range(3):
        if request.form['interval-' + str(n + 1)] == '':
            continue
        else:
            name = request.form['userName']
            day = request.form['interval-' + str(n + 1)].split(' ')[0]
            interval = request.form['interval-' +
                                    str(n + 1)].replace(day + ' ', '')

            conn = get_db_connection()
            selectQuery = f"select * from users where name = '{name}' and day = '{day}' and interval = '{interval}'"
            result = conn.execute(selectQuery).fetchall()
            conn.close()
            if len(result) > 0:
                entryFound = True
                for x in range(len(result)):
                    error = error + ' ' + \
                        result[x][2] + ' ' + result[x][3]
            else:
                success = success + ' ' + day + ' ' + interval + ', '
                pass

            if entryFound == False:

                conn = get_db_connection()
                conn.execute(CREATE_USERS_TABLE)
                conn.execute(INSERT_USERS_RETURN_ID,
                                (name, day, interval))
                conn.commit()
                conn.close()
            else:
                return render_template('index.html', defWeek=defaultWeekday, dates=dates, weekdays=weekdays, intervals=intervals, err=error, success='', top=top3)

    conn = get_db_connection()
    selectQuery = f"select day, interval, count(*) as voturi from users group by 1,2 order by voturi desc limit 3"
    top3 = conn.execute(selectQuery).fetchall()
    conn.close()

    # return redirect(url_for('views.home'))
    return redirect(url_for('views.thanks'))


@views.route('/', methods=['GET', 'POST'])
def home():
    global defaultWeekday, dates, weekdays, today, weekday, intervals, success, top3

    today = datetime.date.today()
    weekday = datetime.datetime.now().isocalendar()[2]
    defaultWeekday = today - datetime.timedelta(days=weekday - 1)

    conn = get_db_connection()
    selectQuery = f"select day, interval, count(*) as voturi from users group by 1,2 order by voturi desc limit 3"
    top3 = conn.execute(selectQuery).fetchall()

    selectQueryI1 = f"select name from users where day = '{top3[0][0]}' and interval = '{top3[0][1]}'"
    userNamesI1 = conn.execute(selectQueryI1).fetchall()

    selectQueryI2 = f"select name from users where day = '{top3[1][0]}' and interval = '{top3[1][1]}'"
    userNamesI2 = conn.execute(selectQueryI2).fetchall()

    selectQueryI3 = f"select name from users where day = '{top3[2][0]}' and interval = '{top3[2][1]}'"
    userNamesI3 = conn.execute(selectQueryI3).fetchall()

    conn.close()

    dates = []
    for n in range(7):
        tempdate = defaultWeekday + datetime.timedelta(days=n)
        tempdate = tempdate.strftime('%d/%m/%Y')
        dates.append(tempdate)
    weekdays = ['Luni', 'Marti', 'Miercuri',
                'Joi', 'Vineri', 'Sambata', 'Duminica']
    intervals = ['12:00 - 14:00', '14:00 - 16:00',
                 '16:00 - 18:00', '18:00 - 20:00']

    return render_template('index.html', defWeek=defaultWeekday, dates=dates, weekdays=weekdays, intervals=intervals, err='', success=success, top=top3, i1=userNamesI1, i2=userNamesI2, i3=userNamesI3)


@views.route('/thank-you')
def thanks():
    global success
    return render_template('thanks.html', success=success)
