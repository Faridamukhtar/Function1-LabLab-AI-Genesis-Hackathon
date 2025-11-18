class MCQScorer:
    """Scores MCQ answers deterministically"""

    def score_mcq_answers(self, mcq_questions, user_answers):
        """
        Score MCQ answers based on correct answers
        
        Args:
        - mcq_questions: List of question objects with 'correct_answer' field
        - user_answers: List of user's answers ['A', 'B', 'C', ...]
        
        Returns: Dict with score, correct_count, total_count
        """
        if not mcq_questions or not user_answers:
            return {
                'score': 50,
                'correct_count': 0,
                'total_count': len(mcq_questions) if mcq_questions else 0
            }

        correct_count = 0
        total_count = len(mcq_questions)

        for i, question in enumerate(mcq_questions):
            if i < len(user_answers):
                correct_answer = question.get("correct_answer", "").strip().upper()
                user_answer = str(user_answers[i]).strip().upper()

                if correct_answer == user_answer:
                    correct_count += 1
                    print(f"   ✓ Q{i+1}: Correct")
                else:
                    print(
                        f"   ✗ Q{i+1}: Incorrect (expected {correct_answer}, got {user_answer})"
                    )

        # Convert to 1-100 score
        percentage = (correct_count / total_count) * 100
        score = max(1, min(100, int(percentage)))

        print(
            f"   MCQ Score: {score}/100 ({correct_count}/{total_count} correct)"
        )
        
        return {
            'score': score,
            'correct_count': correct_count,
            'total_count': total_count
        }