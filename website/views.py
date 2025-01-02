from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Workout
from datetime import datetime, date
from . import db
import json
from dotenv import load_dotenv
import os

load_dotenv()

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    today = date.today()
    # Get page numbers for past and upcoming workouts separately
    past_page = request.args.get("past_page", 1, type=int)
    upcoming_page = request.args.get("upcoming_page", 1, type=int)
    workouts_per_page = int(os.getenv("PAGINATION_SIZE", 6))  # Default to 6 if not set in .env

    # Query for past workouts (date < today) with pagination
    past_workouts = (
        Workout.query.filter(
            Workout.user_id == current_user.id,
            Workout.date < today
        )
        .order_by(Workout.date.desc())
        .paginate(page=past_page, per_page=workouts_per_page)
    )

    # Query for upcoming workouts (date >= today) with pagination
    upcoming_workouts = (
        Workout.query.filter(
            Workout.user_id == current_user.id,
            Workout.date >= today
        )
        .order_by(Workout.date.asc())
        .paginate(page=upcoming_page, per_page=workouts_per_page)
    )

    # Handle form submission
    if request.method == "POST":
        workout_name = request.form.get("workout_name")
        workout_length = request.form.get("workout_length")
        workout_url = request.form.get("workout_url")
        workout_date = request.form.get("workout_date")

        if workout_date:
            workout_date = datetime.strptime(workout_date, "%Y-%m-%d").date()
        else:
            workout_date = None

        length_unit = request.form.get("length_unit")  # "minutes" or "miles"
        is_minutes = length_unit == "minutes"

        if len(workout_name) < 1 or len(workout_length) < 1:
            flash("Workout name and length cannot be empty!", category="error")
        else:
            new_workout = Workout(
                name=workout_name,
                length=workout_length,
                url=workout_url,
                user_id=current_user.id,
                is_minutes=is_minutes,
                date=workout_date,
            )
            db.session.add(new_workout)
            db.session.commit()
            flash("Workout added!", category="success")
            return redirect(url_for("views.home"))

    # Pass the pagination objects to the template
    return render_template(
        "home.html",
        user=current_user,
        past_workouts=past_workouts,
        upcoming_workouts=upcoming_workouts,
        today=today,
    )

@views.route('/delete-workout', methods=['POST'])
def delete_workout():  
    workout = json.loads(request.data)
    workoutId = workout['workoutId']
    workout = Workout.query.get(workoutId)
    if workout:
        if workout.user_id == current_user.id:
            db.session.delete(workout)
            db.session.commit()

    return jsonify({})
