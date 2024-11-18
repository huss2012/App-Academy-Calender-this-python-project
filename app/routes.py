import os
import psycopg2
from flask import Blueprint, render_template, redirect
from datetime import datetime
from app.forms import AppointmentForm

bp = Blueprint('main',__name__, url_prefix='/')


CONNECTION_PARAMTERS = {
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get('DB_PASS'),
    'dbname': os.environ.get('DB_NAME'),
    'host': os.environ.get('DB_HOST')
}


@bp.route("/", methods=["GET", "POST"])
def main():
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
    with psycopg2.connect(**CONNECTION_PARAMTERS) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT id, name, start_datetime, end_datetime FROM appointments ORDER BY start_datetime;")
            rows = curs.fetchall()
            return render_template('main.html', rows=rows, form=form)
