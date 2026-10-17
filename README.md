# 🎓 Student Performance Prediction System
**Final-Year BSc Computer Science (Artificial Intelligence) Project**

An end-to-end Machine Learning web application designed to predict student academic outcomes, identify at-risk students early, and generate actionable academic interventions using multi-factor regression models.

---

## 📌 1. Project Overview

Early intervention is critical in higher education. Faculty and academic mentors often discover that a student is struggling only after final examinations. The **Student Performance Prediction System** bridges this gap by leveraging supervised machine learning to forecast a student's final marks based on early semester indicators—such as lecture attendance, internal assessment scores, assignment quality, study hours, and activity participation.

### Key Objectives:
- **Continuous Mark Prediction:** Accurately forecasts numerical final marks between 0.0 and 100.0%.
- **Performance & Risk Categorization:** Classifies students into **Excellent**, **Good**, **Average**, and **At-Risk** cohorts with risk ratings.
- **Actionable Remedial Guidance:** Synthesizes factor-specific recommendations (e.g. attendance alerts, study hour suggestions) without subjective guesswork.
- **Institutional Analytics:** Visualizes cohort distributions, correlation scatter charts, and risk metrics via Chart.js on an Admin Dashboard.
- **Persistent Student Records:** Stores assessments in SQLite with search, category filtering, and record management.

---

## 🛠️ 2. Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js |
| **Backend** | Python 3.13, Flask 3.1.0 |
| **Machine Learning** | Scikit-learn, Pandas, NumPy, Joblib |
| **Database** | SQLite (Embedded Relational DB with Parameterized Queries) |
| **Environment** | Windows / Cross-platform compatible |

---

## 📂 3. Project Folder Structure

```
Student_Performance_Prediction/
│
├── app.py                          # Main Flask web application and HTTP route handlers
├── train_model.py                  # Model training, evaluation, comparison & persistence
├── model.py                        # Model inference, classification logic & recommendations
├── database.py                     # SQLite database schema, CRUD operations & analytics
├── test_system.py                  # End-to-end automated test suite
├── requirements.txt                # Project dependency specifications
├── README.md                       # Complete documentation & setup guide
│
├── dataset/
│   ├── student_performance.csv     # Synthetic academic training dataset (~1,200 records)
│   └── generate_dataset.py         # Script to regenerate synthetic academic data
│
├── models/
│   ├── student_performance_model.pkl # Serialized best ML regression model (Joblib)
│   └── model_metrics.json          # Comparative metrics (Linear Regression vs Random Forest)
│
├── templates/
│   ├── base.html                   # Base layout with responsive navbar, alerts & footer
│   ├── index.html                  # Landing page with hero banner & workflow highlights
│   ├── predict.html                # Prediction input form with client & server validation
│   ├── result.html                 # Performance assessment report with score gauge & badges
│   ├── dashboard.html              # Admin analytics dashboard with 4 Chart.js charts
│   ├── students.html               # Student records directory with search and filtering
│   ├── student_detail.html         # Detailed individual student profile
│   └── about.html                  # Problem statement, architecture & ML evaluation report
│
├── static/
│   ├── css/
│   │   └── style.css               # Custom design, modern cards, and responsive styling
│   └── js/
│       ├── script.js               # Form validation & UI interactions
│       └── dashboard.js            # Chart.js dynamic data fetching and visualizations
│
└── database/
    └── student_performance.db      # Auto-initialized SQLite database file
```

---

## 📊 4. Dataset Information

- **Dataset File:** `dataset/student_performance.csv`
- **Sample Size:** 1,200 student records
- **Data Nature Disclaimer:** This dataset consists of **synthetic academic data** generated for educational demonstration and development purposes. No real personal student data is used.

### Feature Dictionary:

| Feature Name | Type | Range | Description |
|---|---|---|---|
| `attendance` | Continuous (Float) | 0 – 100% | Total percentage of lectures and labs attended. |
| `internal_marks` | Continuous (Float) | 0 – 100 | Mid-term examinations or continuous assessment scores. |
| `assignment_marks` | Continuous (Float) | 0 – 100 | Continuous evaluation score from homework/practicals. |
| `previous_marks` | Continuous (Float) | 0 – 100 | Academic baseline from preceding semester or prerequisite. |
| `study_hours` | Continuous (Float) | 0 – 24 hrs | Average daily self-study and revision time outside class. |
| `activity_score` | Continuous (Float) | 0 – 100 | Engagement in seminars, tutorials, and class participation. |
| **`final_marks`** (Target) | Continuous (Float) | 0 – 100 | **Predicted final semester score (0–100).** |

---

## 🤖 5. Machine Learning Methodology & Model Evaluation

### Data Preprocessing:
1. Checked and handled missing values using column medians.
2. Verified and removed duplicate rows.
3. Split the dataset: **80% Training Set (960 records)** and **20% Testing Set (240 records)** with a fixed random seed (`random_state=42`) to prevent data leakage.

### Model Comparison & Benchmark Results:

The models were evaluated on the isolated test set using standard regression evaluation metrics:
- **MAE (Mean Absolute Error):** Average absolute difference between predicted and actual marks.
- **MSE (Mean Squared Error):** Average of squared prediction errors.
- **RMSE (Root Mean Squared Error):** Standard deviation of the residuals in marks.
- **$R^2$ Score (Coefficient of Determination):** Proportion of variance explained by the model.

```
====================================================================
                MODEL EVALUATION COMPARISON RESULTS
====================================================================
Metric               | Linear Regression    | Random Forest       
--------------------------------------------------------------------
MAE (Mean Abs Error) | 2.2342 marks         | 2.4549 marks        
MSE (Mean Sq Error)  | 8.2122               | 9.8927              
RMSE (Root MSE)      | 2.8657 marks         | 3.1453 marks        
R² Score (Variance)  | 0.9192 (91.92%)      | 0.9026 (90.26%)     
====================================================================
Selected Superior Model: Linear Regression (Saved to models/student_performance_model.pkl)
```

Both models achieved high predictive capability ($R^2 > 0.90$). The best-performing model is serialized via `joblib` for low-latency live web inference in Flask.

---

## 🎯 6. Performance Classification & Recommendation Rubric

| Predicted Marks Range | Classification | Risk Level | System Recommendation Summary |
|---|---|---|---|
| **75.0 – 100.0** | **Excellent** | Low Risk | *"Excellent performance. Continue maintaining your current academic habits."* |
| **60.0 – 74.9** | **Good** | Low Risk | *"Good performance. Focus on attendance and consistent revision."* |
| **50.0 – 59.9** | **Average** | Medium Risk | *"Your performance can be improved. Increase study hours and assignment performance."* |
| **Below 50.0** | **At Risk** | High Risk | *"Your performance is at risk. Improve attendance, internal marks, assignments and study consistency."* |

Additionally, the system automatically checks for low individual parameters (e.g. attendance $< 75\%$, study hours $< 3$ hrs, internal marks $< 50$) and appends specific constructive steps.

---

## 🚀 7. Installation & Running Guide (Windows Step-by-Step)

### Prerequisites:
- Python 3.10+ installed on your Windows machine.
- Terminal or PowerShell.

### Step 1: Open PowerShell in Project Folder
Open PowerShell or Command Prompt and navigate to the project directory:
```powershell
cd "c:\Users\acer\OneDrive\Desktop\student performance prediction"
```

### Step 2: (Optional) Create & Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Or on Windows Command Prompt (CMD):
.\venv\Scripts\activate.bat
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: (Optional) Generate Dataset & Train Model
The repository already includes the generated dataset and pre-trained model. If you wish to retrain from scratch:
```powershell
# 1. Regenerate dataset
python dataset/generate_dataset.py

# 2. Train and compare models
python train_model.py
```

### Step 5: Launch the Web Application
```powershell
python app.py
```

### Step 6: Open in Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 🧪 8. Automated Testing

To run the full automated test suite covering ML inference, validation rules, database CRUD operations, and Flask routes:

```powershell
python test_system.py
```

Expected output:
```
........
----------------------------------------------------------------------
Ran 8 tests in 0.340s

OK
```

---

## 🖥️ 9. Application Modules & Walkthrough

1. **Home Page (`/`)**: Project presentation, KPI counters, workflow cards, tech stack showcase, and quick access.
2. **Prediction Page (`/predict`)**: Input form with real-time numeric bounds (0–100, 0–24 hrs), quick autofill demo buttons for viva presentations, and client/server validation.
3. **Prediction Result Report (`/result/<id>`)**: Circular score gauge, performance tier badge, risk indicator, multi-variable breakdown bars, tailored recommendation, and print/export feature.
4. **Admin Dashboard (`/dashboard`)**: Institutional metrics and 4 Chart.js charts:
   - Category Breakdown (Doughnut)
   - Attendance vs Score (Scatter)
   - Internal Marks vs Score (Scatter)
   - Grade Distribution (Histogram/Bar)
5. **Student Directory (`/students`)**: Search by student name or roll number, filter by category, view individual student profiles (`/student/<id>`), and delete records with modal confirmation.
6. **About Page (`/about`)**: Detailed academic problem statement, solution benefits, system pipeline, and comparative model evaluation table.

---

## 🔮 10. Future Enhancements

- Integration with University Learning Management Systems (LMS) like Moodle or Canvas via REST APIs.
- Semester-over-semester longitudinal time-series forecasting.
- Automated email/SMS alerts to designated academic mentors for students falling in the *At-Risk* category.
- Multi-class Deep Neural Network (DNN) / XGBoost algorithm comparisons.

---

## 📜 11. Project Metadata

- **Project Title:** Student Performance Prediction System
- **Academic Degree:** BSc Computer Science (Artificial Intelligence)
- **Primary Domain:** Machine Learning & Applied Web Engineering
- **License:** Open Source for Educational Demonstration
