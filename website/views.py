from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Workout
from datetime import datetime, date
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    today = date.today()
    # Get the page number from the URL (default is 1)
    page = request.args.get('page', 1, type=int)
    workouts_per_page = 6  # Display 6 workouts per page
    
    # Query the workouts for the current user and apply pagination
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).paginate(page=page, per_page=workouts_per_page)

    if request.method == 'POST': 
        workout_name = request.form.get('workout_name')
        workout_length = request.form.get('workout_length')
        workout_url = request.form.get('workout_url')
        workout_date = request.form.get('workout_date')
        
        if workout_date:
            workout_date = datetime.strptime(workout_date, '%Y-%m-%d').date()
        else:
            workout_date = None

        # Get the length unit from the radio buttons (either 'minutes' or 'miles')
        length_unit = request.form.get('length_unit')  # This will be either 'minutes' or 'miles'
        is_minutes = length_unit == 'minutes'  # True if 'minutes', False if 'miles'

        # You can add validation for the inputs if needed
        if len(workout_name) < 1 or len(workout_length) < 1:
            flash('Workout name and length cannot be empty!', category='error') 
        else:
            new_workout = Workout(name=workout_name, 
                                  length=workout_length, 
                                  url=workout_url, 
                                  user_id=current_user.id,
                                  is_minutes=is_minutes,
                                  date=workout_date)  # Store the length unit as boolean
            db.session.add(new_workout)  # Add workout to the database 
            db.session.commit()
            flash('Workout added!', category='success')
            return redirect(url_for('views.home'))

    # Pass the workouts pagination object to the template
    return render_template("home.html", user=current_user, workouts=workouts, today=today)

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
