from flask import Flask, render_template, request, redirect, url_for, flash, Response
from database import (init_db, add_candidate, get_all_candidates, get_candidate_by_id,
                      update_candidate, delete_candidate, save_skill_scores,
                      get_skill_scores, get_skill_distribution, export_candidates_csv)
from scoring import calculate_final_score, get_all_scores, get_top5, get_dashboard_stats
import csv
import io

app = Flask(__name__)
app.secret_key = "evalhr_secret_key"

init_db()

def seed_data():
    from database import get_connection
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    conn.close()
    if count == 0:
        sample_candidates = [
            ("C001", "Arun Kumar", "arun@email.com", 3, "Python", "SQL", "B.Tech"),
            ("C002", "Priya Sharma", "priya@email.com", 4, "Java", "Spring Boot", "MCA"),
            ("C003", "Rahul Verma", "rahul@email.com", 2, "Python", "Django", "B.Sc CS"),
            ("C004", "Sneha Patel", "sneha@email.com", 5, "Data Science", "Machine Learning", "M.Tech"),
            ("C005", "Vikram Singh", "vikram@email.com", 1, "JavaScript", "React", "BCA"),
        ]
        for c in sample_candidates:
            add_candidate(*c)

        sample_skills = {
            "C001": {"Python": 8, "SQL": 7, "Problem Solving": 9, "Communication": 6},
            "C002": {"Java": 9, "SQL": 8, "Problem Solving": 7, "Communication": 8},
            "C003": {"Python": 7, "Django": 8, "Problem Solving": 6, "Communication": 7},
            "C004": {"Data Science": 9, "Machine Learning": 9, "Problem Solving": 9, "Communication": 8},
            "C005": {"JavaScript": 7, "React": 8, "Problem Solving": 6, "Communication": 7},
        }
        for cid, skills in sample_skills.items():
            save_skill_scores(cid, skills)

seed_data()


@app.route('/')
def dashboard():
    stats = get_dashboard_stats()
    top5 = get_top5()
    rankings = get_all_scores()
    skill_dist = get_skill_distribution()
    return render_template('dashboard.html',
                           stats=stats, top5=top5,
                           rankings=rankings, skill_dist=skill_dist)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        candidate_id = request.form['candidate_id'].strip()
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        experience = int(request.form['experience'])
        primary_skill = request.form['primary_skill'].strip()
        secondary_skill = request.form['secondary_skill'].strip()
        education = request.form['education'].strip()

        success, message = add_candidate(candidate_id, name, email, experience,
                                         primary_skill, secondary_skill, education)
        if success:
            flash(message, 'success')
            return redirect(url_for('skills_eval') + f'?candidate_id={candidate_id}')
        else:
            flash(message, 'error')

    return render_template('add_candidate.html')


@app.route('/edit/<candidate_id>', methods=['GET', 'POST'])
def edit(candidate_id):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        flash('Candidate not found!', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        experience = int(request.form['experience'])
        primary_skill = request.form['primary_skill'].strip()
        secondary_skill = request.form['secondary_skill'].strip()
        education = request.form['education'].strip()
        update_candidate(candidate_id, name, email, experience,
                         primary_skill, secondary_skill, education)
        flash('Candidate updated successfully!', 'success')
        return redirect(url_for('profile', candidate_id=candidate_id))

    return render_template('add_candidate.html', candidate=candidate, edit_mode=True)


@app.route('/delete/<candidate_id>', methods=['POST'])
def delete(candidate_id):
    delete_candidate(candidate_id)
    flash('Candidate deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/skills', methods=['GET', 'POST'])
def skills_eval():
    candidates = get_all_candidates()
    selected_id = request.args.get('candidate_id') or request.form.get('candidate_id') or (candidates[0]['candidate_id'] if candidates else None)
    existing_scores = {}
    selected_candidate = None

    if selected_id:
        selected_candidate = get_candidate_by_id(selected_id)
        rows = get_skill_scores(selected_id)
        existing_scores = {row['skill_name']: row['score'] for row in rows}

    if request.method == 'POST' and selected_id:
        skills = {}
        skill_names = request.form.getlist('skill_name')
        skill_scores = request.form.getlist('skill_score')
        for name, score in zip(skill_names, skill_scores):
            if name.strip() and score:
                skills[name.strip()] = int(score)
        save_skill_scores(selected_id, skills)
        flash('Skill scores saved successfully!', 'success')
        return redirect(url_for('profile', candidate_id=selected_id))

    default_skills = ["Python", "SQL", "Problem Solving", "Communication"]
    return render_template('skill_evaluation.html',
                           candidates=candidates,
                           selected_id=selected_id,
                           selected_candidate=selected_candidate,
                           existing_scores=existing_scores,
                           default_skills=default_skills)


@app.route('/profile')
@app.route('/profile/<candidate_id>')
def profile(candidate_id=None):
    candidates = get_all_candidates()
    if not candidate_id and candidates:
        candidate_id = candidates[0]['candidate_id']

    candidate = get_candidate_by_id(candidate_id) if candidate_id else None
    skill_scores = get_skill_scores(candidate_id) if candidate_id else []
    final_score = calculate_final_score(candidate_id, candidate['experience']) if candidate else None

    
    rankings = get_all_scores()
    rank = next((r['rank'] for r in rankings if r['candidate_id'] == candidate_id), '-')

    return render_template('profile.html',
                           candidates=candidates,
                           candidate=candidate,
                           skill_scores=skill_scores,
                           final_score=final_score,
                           rank=rank,
                           selected_id=candidate_id)


@app.route('/export')
def export_csv():
    rankings = get_all_scores()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Rank', 'Candidate ID', 'Name', 'Email', 'Experience',
                     'Primary Skill', 'Secondary Skill', 'Education', 'Final Score'])
    for r in rankings:
        writer.writerow([r['rank'], r['candidate_id'], r['name'], r['email'],
                         r['experience'], r['primary_skill'], r['secondary_skill'],
                         r['education'], r['final_score'] if r['final_score'] else 'Not Evaluated'])
    output.seek(0)
    return Response(output, mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=candidates.csv"})

if __name__ == '__main__':
    app.run(debug=True)
