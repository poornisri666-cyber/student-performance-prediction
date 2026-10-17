"""
Dataset Generator for Student Performance Prediction System
Generates a realistic synthetic dataset for ML model training and evaluation.
Disclaimer: This dataset consists of synthetic academic data designed for educational demonstration.
"""

import os
import numpy as np
import pandas as pd

def generate_student_dataset(num_samples: int = 1200, random_state: int = 42) -> pd.DataFrame:
    np.random.seed(random_state)
    
    # 1. Study Hours per day (0.5 to 10 hours)
    study_hours = np.random.gamma(shape=3.0, scale=1.2, size=num_samples)
    study_hours = np.clip(study_hours, 0.5, 12.0).round(1)
    
    # 2. Attendance percentage (40% to 100%)
    # Students who study more tend to have slightly better attendance
    attendance_base = np.random.normal(loc=75, scale=12, size=num_samples)
    attendance = attendance_base + (study_hours * 1.5)
    attendance = np.clip(attendance, 35.0, 100.0).round(1)
    
    # 3. Previous Semester Marks (30 to 100)
    previous_marks_base = np.random.normal(loc=65, scale=14, size=num_samples)
    previous_marks = previous_marks_base + (study_hours * 1.2) + (attendance * 0.1)
    previous_marks = np.clip(previous_marks, 30.0, 100.0).round(1)
    
    # 4. Internal Assessment Marks (25 to 100)
    internal_marks_base = (0.45 * previous_marks) + (0.25 * attendance) + (2.0 * study_hours)
    internal_noise = np.random.normal(loc=0, scale=4.5, size=num_samples)
    internal_marks = np.clip(internal_marks_base + internal_noise, 25.0, 100.0).round(1)
    
    # 5. Assignment Marks (25 to 100)
    assignment_base = (0.35 * previous_marks) + (0.30 * attendance) + (2.5 * study_hours)
    assignment_noise = np.random.normal(loc=0, scale=4.0, size=num_samples)
    assignment_marks = np.clip(assignment_base + assignment_noise, 25.0, 100.0).round(1)
    
    # 6. Participation / Activity Score (20 to 100)
    activity_base = np.random.normal(loc=68, scale=15, size=num_samples)
    activity_score = np.clip(activity_base + (attendance * 0.1), 20.0, 100.0).round(1)
    
    # 7. Final Marks (Target Variable)
    # Realistic multi-factor weighted academic formula with interaction effects and slight non-linear diminishing returns
    study_bonus = 2.8 * np.log1p(study_hours) * 1.8
    final_marks_calculated = (
        0.30 * internal_marks +
        0.22 * assignment_marks +
        0.24 * previous_marks +
        0.14 * attendance +
        0.06 * activity_score +
        study_bonus +
        np.random.normal(loc=0, scale=2.8, size=num_samples)
    )
    final_marks = np.clip(final_marks_calculated, 15.0, 100.0).round(1)
    
    df = pd.DataFrame({
        "attendance": attendance,
        "internal_marks": internal_marks,
        "assignment_marks": assignment_marks,
        "previous_marks": previous_marks,
        "study_hours": study_hours,
        "activity_score": activity_score,
        "final_marks": final_marks
    })
    
    return df

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "student_performance.csv")
    
    os.makedirs(base_dir, exist_ok=True)
    df = generate_student_dataset(num_samples=1200, random_state=42)
    df.to_csv(output_path, index=False)
    
    print(f"Dataset generated successfully at: {output_path}")
    print(f"Shape: {df.shape}")
    print("\nDataset Sample:")
    print(df.head())
    print("\nStatistical Summary:")
    print(df.describe())

if __name__ == "__main__":
    main()
