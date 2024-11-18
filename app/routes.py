import os
import psycopg2
from flask import Blueprint, render_template, redirect, url_for, request
from datetime import datetime, timedelta
from app.forms import AppointmentForm, SelectedDates

bp = Blueprint('main', __name__, url_prefix='/')

CONNECTION_PARAMETERS = {
    'user': os.environ.get("DB_USER"),
    'password': os.environ.get("DB_PASS"),
    'dbname': os.environ.get("DB_NAME"),
    'host': os.environ.get("DB_HOST")
}

@bp.route('/<int:year>/<int:month>/<int:day>', methods=["GET", "POST"])
def daily(year, month, day):
    # Initialize forms
    selectingDateForm = SelectedDates()
    form = AppointmentForm()

    # Determine which form is submitted
    if selectingDateForm.submit.data and selectingDateForm.validate_on_submit():
        selected_date = selectingDateForm.selected_date.data
        return redirect(url_for('.daily', year=selected_date.year, month=selected_date.month, day=selected_date.day))

    if form.submit.data and form.validate_on_submit():
        print("Form validation successful")
        params = {
            'name': form.name.data,
            'start_datetime': datetime.combine(form.start_date.data, form.start_time.data),
            'end_datetime': datetime.combine(form.end_date.data, form.end_time.data),
            'description': form.description.data,
            'private': form.private.data
        }
        print(params)
        # Insert data into the database
        with psycopg2.connect(**CONNECTION_PARAMETERS) as conn:
            with conn.cursor() as curs:
                curs.execute("""
                    INSERT INTO appointments
                    (name, start_datetime, end_datetime, description, private)
                    VALUES
                    (%(name)s, %(start_datetime)s, %(end_datetime)s, %(description)s, %(private)s)
                """, params)
            conn.commit()
        # Redirect to the same date page after submission
        return redirect(url_for('.daily', year=year, month=month, day=day))

    # Compute day range for the appointments
    day_start = datetime(year=year, month=month, day=day)
    next_day = day_start + timedelta(days=1)

    # Fetch appointments from the database
    with psycopg2.connect(**CONNECTION_PARAMETERS) as conn:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT
                    id, name, start_datetime, end_datetime
                FROM
                    appointments
                WHERE
                    start_datetime BETWEEN %(day_start)s AND %(next_day)s
                ORDER BY
                    start_datetime
            """, {
                "day_start": day_start,
                "next_day": next_day
            })
            rows = curs.fetchall()

    # Render the template with both forms
    return render_template('main.html', rows=rows, form=form, selectingDateForm=selectingDateForm)

@bp.route("/")
def main():
    current_date = datetime.now()
    return redirect(url_for('.daily', year=current_date.year, month=current_date.month, day=current_date.day))
