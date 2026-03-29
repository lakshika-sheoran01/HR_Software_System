# Candidate Evaluation Dashboard

A Python Flask web application for HR representatives to manage candidate profiles and evaluate candidates based on their skills and experience.

## Features

- **Add Candidates** — Register candidates with ID, name, email, experience, skills, and education
- **Skill Evaluation** — Assign skill scores (1–10) per candidate using interactive sliders
- **Score Calculation** — Automatically calculates final score using the formula:
  > `Final Score = (Average Skill Score × 0.7) + (Experience × 0.3)`
- **Dashboard** — View total candidates, average experience, top 5 rankings, and skill distribution chart
- **Candidate Profile** — Detailed view with skill scores, final score, and ranking
- **Edit & Delete** — Modify or remove candidate records
- **Export CSV** — Download all candidate data as a CSV file
- **Filter by Skill** — View skill distribution on dashboard

## Project Structure

```
candidate_dashboard/
├── app.py            
├── database.py       
├── scoring.py        
├── candidates.db     
├── requirements.txt  
├── README.md        
└── templates/
    ├── base.html           
    ├── dashboard.html      
    ├── add_candidate.html  
    ├── skill_evaluation.html 
    └── profile.html        
```

## Setup Instructions (Windows)

### Step 1 — Make sure Python is installed
```
python --version
```

### Step 2 — Open project folder in VSCode
- Open VSCode → File → Open Folder → select `candidate_dashboard`

### Step 3 — Create and activate virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### Step 4 — Install dependencies
```
pip install -r requirements.txt
```

### Step 5 — Run the application
```
python app.py
```

### Step 6 — Open in browser
Go to: **http://127.0.0.1:5000**

## Database Design

**Table: candidates**
| Column | Type |
|---|---|
| candidate_id | TEXT (Primary Key) |
| name | TEXT |
| email | TEXT |
| experience | INTEGER |
| primary_skill | TEXT |
| secondary_skill | TEXT |
| education | TEXT |

**Table: skill_scores**
| Column | Type |
|---|---|
| id | INTEGER (Primary Key) |
| candidate_id | TEXT (Foreign Key) |
| skill_name | TEXT |
| score | INTEGER |

