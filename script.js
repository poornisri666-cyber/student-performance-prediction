/**
 * Student Performance Prediction System
 * General Client-Side Script
 */

document.addEventListener("DOMContentLoaded", function () {
    // 1. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll(".alert-dismissible");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                // Ignore if already dismissed
            }
        }, 6000);
    });

    // 2. Prediction Form Validation
    const form = document.getElementById("predictionForm");
    if (form) {
        form.addEventListener("submit", function (event) {
            let isValid = true;
            let errorMessage = "";

            const name = document.getElementById("student_name").value.trim();
            const sid = document.getElementById("student_id").value.trim();
            const att = parseFloat(document.getElementById("attendance").value);
            const internal = parseFloat(document.getElementById("internal_marks").value);
            const assignment = parseFloat(document.getElementById("assignment_marks").value);
            const previous = parseFloat(document.getElementById("previous_marks").value);
            const study = parseFloat(document.getElementById("study_hours").value);
            const activity = parseFloat(document.getElementById("activity_score").value);

            if (!name) {
                isValid = false;
                errorMessage = "Please enter the Student Full Name.";
            } else if (!sid) {
                isValid = false;
                errorMessage = "Please enter the Student ID.";
            } else if (isNaN(att) || att < 0 || att > 100) {
                isValid = false;
                errorMessage = "Attendance Percentage must be between 0.0% and 100.0%.";
            } else if (isNaN(internal) || internal < 0 || internal > 100) {
                isValid = false;
                errorMessage = "Internal Assessment Marks must be between 0.0 and 100.0.";
            } else if (isNaN(assignment) || assignment < 0 || assignment > 100) {
                isValid = false;
                errorMessage = "Assignment Marks must be between 0.0 and 100.0.";
            } else if (isNaN(previous) || previous < 0 || previous > 100) {
                isValid = false;
                errorMessage = "Previous Semester Marks must be between 0.0 and 100.0.";
            } else if (isNaN(study) || study < 0 || study > 24) {
                isValid = false;
                errorMessage = "Daily Study Hours must be between 0.0 and 24.0 hours.";
            } else if (isNaN(activity) || activity < 0 || activity > 100) {
                isValid = false;
                errorMessage = "Participation/Activity Score must be between 0.0 and 100.0.";
            }

            if (!isValid) {
                event.preventDefault();
                alert(errorMessage);
            } else {
                // Show loading state on button
                const btn = document.getElementById("btnPredict");
                if (btn) {
                    btn.disabled = true;
                    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Calculating Prediction...';
                }
            }
        });
    }
});
