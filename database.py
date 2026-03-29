import sqlite3

DB_NAME = "candidates.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            experience INTEGER NOT NULL,
            primary_skill TEXT NOT NULL,
            secondary_skill TEXT,
            education TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skill_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
        )
    ''')

    conn.commit()
    conn.close()


def add_candidate(candidate_id, name, email, experience, primary_skill, secondary_skill, education):
    conn = get_connection()
    try:
        conn.execute('''
            INSERT INTO candidates (candidate_id, name, email, experience, primary_skill, secondary_skill, education)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (candidate_id, name, email, experience, primary_skill, secondary_skill, education))
        conn.commit()
        return True, "Candidate added successfully!"
    except sqlite3.IntegrityError:
        return False, "Candidate ID already exists!"
    finally:
        conn.close()

def get_all_candidates():
    conn = get_connection()
    candidates = conn.execute('SELECT * FROM candidates ORDER BY name').fetchall()
    conn.close()
    return candidates

def get_candidate_by_id(candidate_id):
    conn = get_connection()
    candidate = conn.execute('SELECT * FROM candidates WHERE candidate_id = ?', (candidate_id,)).fetchone()
    conn.close()
    return candidate

def update_candidate(candidate_id, name, email, experience, primary_skill, secondary_skill, education):
    conn = get_connection()
    conn.execute('''
        UPDATE candidates SET name=?, email=?, experience=?, primary_skill=?, secondary_skill=?, education=?
        WHERE candidate_id=?
    ''', (name, email, experience, primary_skill, secondary_skill, education, candidate_id))
    conn.commit()
    conn.close()

def delete_candidate(candidate_id):
    conn = get_connection()
    conn.execute('DELETE FROM skill_scores WHERE candidate_id = ?', (candidate_id,))
    conn.execute('DELETE FROM candidates WHERE candidate_id = ?', (candidate_id,))
    conn.commit()
    conn.close()


def save_skill_scores(candidate_id, skills_dict):
    conn = get_connection()
    conn.execute('DELETE FROM skill_scores WHERE candidate_id = ?', (candidate_id,))
    for skill_name, score in skills_dict.items():
        conn.execute('''
            INSERT INTO skill_scores (candidate_id, skill_name, score)
            VALUES (?, ?, ?)
        ''', (candidate_id, skill_name, int(score)))
    conn.commit()
    conn.close()

def get_skill_scores(candidate_id):
    conn = get_connection()
    scores = conn.execute(
        'SELECT skill_name, score FROM skill_scores WHERE candidate_id = ? ORDER BY skill_name',
        (candidate_id,)
    ).fetchall()
    conn.close()
    return scores

def get_all_skill_scores():
    conn = get_connection()
    scores = conn.execute('SELECT * FROM skill_scores').fetchall()
    conn.close()
    return scores

def get_skill_distribution():
    conn = get_connection()
    dist = conn.execute('''
        SELECT primary_skill, COUNT(*) as count
        FROM candidates
        GROUP BY primary_skill
        ORDER BY count DESC
    ''').fetchall()
    conn.close()
    return dist

def export_candidates_csv():
    conn = get_connection()
    candidates = conn.execute('SELECT * FROM candidates').fetchall()
    conn.close()
    return candidates
