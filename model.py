"""
Model Inference, Performance Classification & Recommendation Engine
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

FEATURE_NAMES = [
    "attendance",
    "internal_marks",
    "assignment_marks",
    "previous_marks",
    "study_hours",
    "activity_score"
]

class StudentPredictor:
    def __init__(self, model_path: str = None, metrics_path: str = None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = model_path or os.path.join(base_dir, "models", "student_performance_model.pkl")
        self.metrics_path = metrics_path or os.path.join(base_dir, "models", "model_metrics.json")
        self.model = None
        self.metrics = None
        self.load_model()

    def is_model_loaded(self) -> bool:
        return self.model is not None

    def load_model(self):
        """Loads the serialized ML model and metrics if available."""
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception as e:
                print(f"[ERROR] Failed to load model from {self.model_path}: {e}")
                self.model = None
        else:
            self.model = None
            
        if os.path.exists(self.metrics_path):
            try:
                with open(self.metrics_path, "r", encoding="utf-8") as f:
                    self.metrics = json.load(f)
            except Exception as e:
                print(f"[WARNING] Failed to load metrics from {self.metrics_path}: {e}")
                self.metrics = None

    def predict(self, input_data: dict) -> float:
        """
        Takes dictionary of student features, passes through ML model,
        and returns predicted final marks rounded to 2 decimal places.
        """
        if self.model is None:
            self.load_model()
            if self.model is None:
                raise FileNotFoundError(
                    "Trained ML model not found. Please run 'python train_model.py' to train the model first."
                )

        # Prepare feature vector in exact order
        try:
            feature_values = [
                float(input_data["attendance"]),
                float(input_data["internal_marks"]),
                float(input_data["assignment_marks"]),
                float(input_data["previous_marks"]),
                float(input_data["study_hours"]),
                float(input_data["activity_score"])
            ]
        except (KeyError, ValueError, TypeError) as err:
            raise ValueError(f"Invalid or missing feature values: {err}")

        # Input array for scikit-learn
        df_input = pd.DataFrame([feature_values], columns=FEATURE_NAMES)
        predicted_score = float(self.model.predict(df_input)[0])

        # Clip predicted score within realistic academic bounds [0.0, 100.0]
        predicted_score = max(0.0, min(100.0, predicted_score))
        return round(predicted_score, 2)

    @staticmethod
    def classify_performance(marks: float) -> tuple[str, str, str, str]:
        """
        Classifies performance category and risk level based on final marks.
        Returns: (category, risk_level, badge_class, color_hex)
        """
        if marks >= 75.0:
            return ("Excellent", "Low Risk", "success", "#198754")
        elif marks >= 60.0:
            return ("Good", "Low Risk", "info", "#0dcaf0")
        elif marks >= 50.0:
            return ("Average", "Medium Risk", "warning", "#ffc107")
        else:
            return ("At Risk", "High Risk", "danger", "#dc3545")

    @staticmethod
    def generate_recommendations(features: dict, predicted_marks: float, category: str) -> str:
        """
        Generates safe, constructive, academic improvement recommendations
        based on category and specific weak areas.
        """
        # Primary base recommendation according to specifications
        if category == "Excellent":
            base_rec = "Excellent performance. Continue maintaining your current academic habits."
        elif category == "Good":
            base_rec = "Good performance. Focus on attendance and consistent revision."
        elif category == "Average":
            base_rec = "Your performance can be improved. Increase study hours and assignment performance."
        else: # At Risk
            base_rec = "Your performance is at risk. Improve attendance, internal marks, assignments and study consistency."

        # Targeted factor-specific suggestions
        specific_tips = []
        
        att = float(features.get("attendance", 100))
        if att < 75.0:
            specific_tips.append(f"Raise attendance from {att:.1f}% to at least 75% to meet institution requirements.")
            
        study_h = float(features.get("study_hours", 4))
        if study_h < 3.0:
            specific_tips.append(f"Increase daily self-study from {study_h:.1f} hrs to 3.5-5.0 hrs for thorough concept retention.")
            
        internals = float(features.get("internal_marks", 100))
        if internals < 50.0:
            specific_tips.append(f"Seek instructor clarification on internal assessment feedback (current: {internals:.1f}/100).")
            
        assign = float(features.get("assignment_marks", 100))
        if assign < 60.0:
            specific_tips.append(f"Submit assignments earlier and utilize rubric guidelines (current: {assign:.1f}/100).")

        if specific_tips:
            full_rec = f"{base_rec} Targeted Action Steps: " + " | ".join(specific_tips)
        else:
            full_rec = base_rec

        return full_rec

# Global singleton predictor instance
predictor = StudentPredictor()
