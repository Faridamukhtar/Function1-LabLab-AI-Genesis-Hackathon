def calculate_mcq_score(mcq_questions, candidate_answers):
    total = len(mcq_questions)
    correct = 0
    
    for question, answer in zip(mcq_questions, candidate_answers):
        if answer.upper() == question["correct_answer"].upper():
            correct += 1
    
    score = int((correct / total) * 100) if total > 0 else 0
    
    return {
        "mcq_score": max(1, score),
        "correct_count": correct,
        "total_count": total,
        "accuracy": round((correct / total) * 100, 1) if total > 0 else 0
    }