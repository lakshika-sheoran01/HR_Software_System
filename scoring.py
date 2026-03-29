from database import get_all_candidates, get_skill_scores

def calculate_final_score(candidate_id, experience):
    """
    Formula: Final Score = (Average Skill Score x 0.7) + (Experience x 0.3)
    """
    scores = get_skill_scores(candidate_id)

    if not scores:
        return None  

    total = sum(row['score'] for row in scores)
    avg_skill_score = total / len(scores)

    final_score = (avg_skill_score * 0.7) + (experience * 0.3)
    return round(final_score, 2)

def get_all_scores():
    """Returns list of all candidates with their final scores, sorted by rank."""
    candidates = get_all_candidates()
    results = []

    for c in candidates:
        score = calculate_final_score(c['candidate_id'], c['experience'])
        results.append({
            'candidate_id': c['candidate_id'],
            'name': c['name'],
            'email': c['email'],
            'experience': c['experience'],
            'primary_skill': c['primary_skill'],
            'secondary_skill': c['secondary_skill'],
            'education': c['education'],
            'final_score': score
        })

    evaluated = sorted([r for r in results if r['final_score'] is not None], key=lambda x: x['final_score'], reverse=True)
    not_evaluated = [r for r in results if r['final_score'] is None]

    ranked = []
    for i, r in enumerate(evaluated):
        r['rank'] = i + 1
        ranked.append(r)
    for r in not_evaluated:
        r['rank'] = '-'
        ranked.append(r)

    return ranked

def get_top5():
    """Returns top 5 candidates by final score."""
    all_scores = get_all_scores()
    evaluated = [r for r in all_scores if r['final_score'] is not None]
    return evaluated[:5]

def get_dashboard_stats():
    """Returns summary statistics for dashboard."""
    candidates = get_all_candidates()
    total = len(candidates)

    if total == 0:
        return {
            'total': 0,
            'avg_experience': 0,
            'highest_score': None,
            'evaluated_count': 0
        }

    avg_exp = round(sum(c['experience'] for c in candidates) / total, 1)

    all_scores = get_all_scores()
    evaluated = [r for r in all_scores if r['final_score'] is not None]
    evaluated_count = len(evaluated)
    highest_score = evaluated[0]['final_score'] if evaluated else None

    return {
        'total': total,
        'avg_experience': avg_exp,
        'highest_score': highest_score,
        'evaluated_count': evaluated_count
    }
