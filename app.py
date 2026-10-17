"""
Student Performance Prediction System - Flask Web Application
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
from model import predictor

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "student-performance-ai-secret-key-2026")

# Initialize SQLite database on startup
database.init_db()

@app.context_processor
def inject_global_context():
    """Provides common context variables across all templates."""
    return {
        "model_loaded": predictor.is_model_loaded(),
        "current_year": 2026
    }

@app.route("/")
def index():
    """Landing Home Page."""
    stats = database.get_dashboard_stats()
    metrics = predictor.metrics
    return render_template("index.html", stats=stats, metrics=metrics)

@app.route("/predict", methods=["GET", "POST"])
def predict():
    """Student Performance Prediction Form & Processing."""
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        student_id = request.form.get("student_id", "").strip()
        
        # Form field validation
        if not student_name or not student_id:
            flash("Student Name and Student ID are required.", "danger")
            return render_template("predict.html", form_data=request.form)

        try:
            attendance = float(request.form.get("attendance", -1))
            internal_marks = float(request.form.get("internal_marks", -1))
            assignment_marks = float(request.form.get("assignment_marks", -1))
            previous_marks = float(request.form.get("previous_marks", -1))
            study_hours = float(request.form.get("study_hours", -1))
            activity_score = float(request.form.get("activity_score", -1))
        except (ValueError, TypeError):
            flash("Please enter valid numeric values for all academic fields.", "danger")
            return render_template("predict.html", form_data=request.form)

        # Range Validations
        if not (0.0 <= attendance <= 100.0):
            flash("Please enter a valid attendance percentage between 0 and 100.", "danger")
            return render_template("predict.html", form_data=request.form)

        if not (0.0 <= internal_marks <= 100.0):
            flash("Internal Assessment Marks must be between 0 and 100.", "danger")
            return render_template("predict.html", form_data=request.form)

        if not (0.0 <= assignment_marks <= 100.0):
            flash("Assignment Marks must be between 0 and 100.", "danger")
            return render_template("predict.html", form_data=request.form)

        if not (0.0 <= previous_marks <= 100.0):
            flash("Previous Semester Marks must be between 0 and 100.", "danger")
            return render_template("predict.html", form_data=request.form)

        if not (0.0 <= study_hours <= 24.0):
            flash("Study Hours per day must be between 0 and 24 hours.", "danger")
            return render_template("predict.html", form_data=request.form)

        if not (0.0 <= activity_score <= 100.0):
            flash("Participation/Activity Score must be between 0 and 100.", "danger")
            return render_template("predict.html", form_data=request.form)

        # Prepare feature dictionary for prediction
        feature_dict = {
            "attendance": attendance,
            "internal_marks": internal_marks,
            "assignment_marks": assignment_marks,
            "previous_marks": previous_marks,
            "study_hours": study_hours,
            "activity_score": activity_score
        }

        # ML Model Inference
        try:
            predicted_marks = predictor.predict(feature_dict)
        except FileNotFoundError:
            flash("ML Model file is missing. Please run 'python train_model.py' to train and save the model.", "danger")
            return render_template("predict.html", form_data=request.form)
        except Exception as e:
            flash(f"An error occurred during prediction inference: {e}", "danger")
            return render_template("predict.html", form_data=request.form)

        # Performance Classification & Actionable Recommendations
        category, risk_level, badge_class, color_hex = predictor.classify_performance(predicted_marks)
        recommendation = predictor.generate_recommendations(feature_dict, predicted_marks, category)

        # Persist record into SQLite
        record_id = database.insert_student({
            "student_name": student_name,
            "student_id": student_id,
            "attendance": attendance,
            "internal_marks": internal_marks,
            "assignment_marks": assignment_marks,
            "previous_marks": previous_marks,
            "study_hours": study_hours,
            "activity_score": activity_score,
            "predicted_marks": predicted_marks,
            "performance_category": category,
            "risk_level": risk_level,
            "recommendation": recommendation
        })

        flash(f"Prediction generated successfully for {student_name} (ID: {student_id})!", "success")
        return redirect(url_for("result", student_pk=record_id))

    return render_template("predict.html", form_data={})

@app.route("/result/<int:student_pk>")
def result(student_pk):
    """Prediction Result Detail Page."""
    student = database.get_student_by_id(student_pk)
    if not student:
        flash("Student prediction record not found.", "warning")
        return redirect(url_for("predict"))
    
    # Classification details for badge styling
    category, risk_level, badge_class, color_hex = predictor.classify_performance(student["predicted_marks"])
    return render_template(
        "result.html", 
        student=student, 
        badge_class=badge_class, 
        color_hex=color_hex
    )

@app.route("/dashboard")
def dashboard():
    """Admin & Analytics Dashboard with KPIs and Charts."""
    stats = database.get_dashboard_stats()
    metrics = predictor.metrics
    return render_template("dashboard.html", stats=stats, metrics=metrics)

@app.route("/api/chart-data")
def chart_data():
    """JSON API endpoint returning data series for Chart.js."""
    data = database.get_chart_data()
    return jsonify(data)

@app.route("/students")
def students():
    """Student Records Directory with Search and Category Filter."""
    search_query = request.args.get("search", "").strip()
    category_filter = request.args.get("category", "All").strip()
    
    student_list = database.get_all_students(
        search=search_query if search_query else None,
        category=category_filter if category_filter != "All" else None
    )
    
    return render_template(
        "students.html",
        students=student_list,
        search_query=search_query,
        selected_category=category_filter,
        total_count=len(student_list)
    )

@app.route("/student/<int:student_pk>")
def student_detail(student_pk):
    """Detailed Individual Student Record Profile."""
    student = database.get_student_by_id(student_pk)
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for("students"))
    
    category, risk_level, badge_class, color_hex = predictor.classify_performance(student["predicted_marks"])
    return render_template(
        "student_detail.html",
        student=student,
        badge_class=badge_class,
        color_hex=color_hex
    )

@app.route("/delete/<int:student_pk>", methods=["POST"])
def delete_student(student_pk):
    """Delete a student record."""
    student = database.get_student_by_id(student_pk)
    if not student:
        flash("Record does not exist or has already been removed.", "warning")
    else:
        name = student["student_name"]
        sid = student["student_id"]
        success = database.delete_student_by_id(student_pk)
        if success:
            flash(f"Record for {name} ({sid}) has been successfully deleted.", "success")
        else:
            flash("Could not delete the record. Please try again.", "danger")
            
    return redirect(request.referrer or url_for("students"))

@app.route("/about")
def about():
    """About Page: Problem, Solution, Benefits, Architecture & ML Metrics."""
    metrics = predictor.metrics
    return render_template("about.html", metrics=metrics)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("base.html", error_title="404 - Page Not Found", error_message="The requested page could not be located."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("base.html", error_title="500 - Server Error", error_message="An internal error occurred. Please check the logs."), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
