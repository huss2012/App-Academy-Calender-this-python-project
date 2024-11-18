import os
import psycopg2
from flask import Blueprint, render_template, redirect, url_for
from datetime import datetime, timedelta
from app.forms import AppointmentForm

bp = Blueprint('main',__name__, url_prefix='/')


CONNECTION_PARAMTERS = {
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get('DB_PASS'),
    'dbname': os.environ.get('DB_NAME'),
    'host': os.environ.get('DB_HOST')
}

@bp.route('/<int:year>/<int:month>/<int:day>', methods=["GET", "POST"])
def daily(year, month, day):
    form = AppointmentForm()

    if form.validate_on_submit():
        print("Form validation successfully")
        params = {
            'name': form.name.data,
            'start_datetime': datetime.combine(form.start_date.data, form.start_time.data),
            'end_datetime': datetime.combine(form.end_date.data, form.end_time.data),
            'description': form.description.data,
            'private': form.private.data
        }
        print(params)
        with psycopg2.connect(**CONNECTION_PARAMTERS) as conn:
            with conn.cursor() as curs:
                curs.execute("""
                             INSERT INTO appointments
                             (name, start_datetime, end_datetime, description, private)
                             VALUES
                             (%(name)s, %(start_datetime)s, %(end_datetime)s, %(description)s, %(private)s)
                             """,
                            params)
            conn.commit()
        return redirect('/')

    day = datetime(year=year, month=month, day=day)
    next_day = day + timedelta(days=1)

    with psycopg2.connect(**CONNECTION_PARAMTERS) as conn:
        with conn.cursor() as curs:
            curs.execute("""
                         SELECT
                            id, name, start_datetime, end_datetime
                         FROM
                            appointments
                         WHERE
                            start_datetime
                        BETWEEN
                            %(day)s AND %(next_day)s
                         ORDER BY
                            start_datetime;
                         """, {
                             "day": day,
                             "next_day": next_day
                         })
            rows = curs.fetchall()
            return render_template('main.html', rows=rows, form=form)


@bp.route("/")
def main():
    currentDate = datetime.now()

    return redirect(url_for('.daily', year=currentDate.year, month=currentDate.month, day=currentDate.day))
