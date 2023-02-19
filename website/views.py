import os
import psycopg2
from dotenv import load_dotenv
from flask import render_template, request, redirect, url_for, Blueprint
import datetime

CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT, day TEXT, interval TEXT)"
)

INSERT_USERS_RETURN_ID = "INSERT INTO users (name, day, interval) VALUES (%s, %s, %s) RETURNING id;"

load_dotenv()
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

views = Blueprint('views', __name__)

today = datetime.date.today()
weekday = datetime.datetime.now().isocalendar()[2]
defaultWeekday = today - datetime.timedelta(days=weekday - 1)

success = ''


@views.route('/api/users', methods=['POST'])
def create_users():
    global success
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
            with connection:
                with connection.cursor() as cursor:
                    selectQuery = f"select * from users where name = '{name}' and day = '{day}' and interval = '{interval}'"
                    cursor.execute(selectQuery)
                    result = cursor.fetchall()

                    if len(result) > 0:
                        entryFound = True
                        for x in range(len(result)):
                            error = error + ' ' + \
                                result[x][2] + ' ' + result[x][3]
                    else:
                        success = success + ' ' + day + ' ' + interval
                        continue

    if entryFound == False:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
                cursor.execute(INSERT_USERS_RETURN_ID,
                               (name, day, interval))
                user_id = cursor.fetchone()[0]
    else:
        return render_template('index.html', defWeek=defaultWeekday, dates=dates, weekdays=weekdays, intervals=intervals, err=error, success='')

    # return redirect(url_for('views.home'))
    return redirect(url_for('views.thanks'))


@views.route('/', methods=['GET', 'POST'])
def home():
    global defaultWeekday, dates, weekdays, intervals, success

    dates = []
    for n in range(7):
        tempdate = defaultWeekday + datetime.timedelta(days=n)
        tempdate = tempdate.strftime('%d/%m/%Y')
        dates.append(tempdate)
    weekdays = ['Luni', 'Marti', 'Miercuri',
                'Joi', 'Vineri', 'Sambata', 'Duminica']
    intervals = ['12:00 - 14:00', '14:00 - 16:00',
                 '16:00 - 18:00', '18:00 - 20:00']

    return render_template('index.html', defWeek=defaultWeekday, dates=dates, weekdays=weekdays, intervals=intervals, err='', success=success)


@views.route('/thank-you')
def thanks():
    global success
    return render_template('thanks.html', success=success)
