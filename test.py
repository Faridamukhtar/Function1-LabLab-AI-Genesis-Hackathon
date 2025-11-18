"""
Complete test script for AI Candidate Evaluation System
Gemini + Qdrant only
"""
import json
import sys
from app.pipeline import CandidateEvaluationPipeline

def test_complete_evaluation():
    """
    Test complete evaluation pipeline with sample data
    """
    print("="*80)
    print("AI CANDIDATE EVALUATION SYSTEM - COMPLETE TEST")
    print("Gemini + Qdrant Pipeline")
    print("="*80)
    
    # Job requirements
    jd_text = """
    Senior Backend Engineer
    Requirements:
    - 5+ years Python backend development
    - Experience with microservices architecture
    - Strong knowledge of AWS cloud services
    - Database optimization expertise
    - RESTful API design
    - System design and scalability
    """
    
    ideal_candidate_profile = """
    Perfect candidate has:
    - 5+ years Python experience with FastAPI/Django
    - Microservices architecture and design patterns
    - AWS services (EC2, Lambda, RDS, S3)
    - PostgreSQL and Redis optimization
    - Strong communication and technical leadership
    - Problem-solving mindset
    """
    
    task_description = """
    Build a REST API endpoint that returns the top K most frequent elements from a list.
    Requirements:
    - Handle edge cases (empty list, invalid K)
    - Optimal time complexity
    - Production-ready code quality
    """
    
    candidate_id = "john_doe_test_001"
    jd_id = "backend_senior_2025"
    
    # Initialize pipeline
    pipeline = CandidateEvaluationPipeline(
        jd_text=jd_text,
        ideal_candidate_profile=ideal_candidate_profile,
        task_description=task_description,
        candidate_id=candidate_id,
        jd_id=jd_id
    )
    
    # Sample code submission
    code_solution = """
from collections import Counter
from typing import List

def top_k_frequent(nums: List[int], k: int) -> List[int]:
    '''
    Returns the top K most frequent elements from a list.
    Time: O(n + m log m) where m = unique elements
    Space: O(n)
    '''
    if not nums or k <= 0:
        return []
    
    counter = Counter(nums)
    return [num for num, _ in counter.most_common(k)]

# Test cases
assert top_k_frequent([1,1,1,2,2,3], 2) == [1, 2]
assert top_k_frequent([1], 1) == [1]
assert top_k_frequent([], 1) == []
"""
    
    # Sample resume
    resume_text = """
John Doe
Senior Software Engineer

EXPERIENCE:
TechCorp Inc. (2018-2025) - Senior Backend Engineer
- Built microservices handling 1M+ requests/day using Python FastAPI
- Designed and implemented RESTful APIs with PostgreSQL and Redis caching
- Led AWS infrastructure migration (EC2, Lambda, RDS, S3)
- Optimized database queries reducing latency by 60%
- Mentored team of 4 junior engineers

StartupXYZ (2016-2018) - Backend Developer
- Developed Python backend services with Django
- Implemented payment processing integrations
- Database design and optimization

SKILLS:
Languages: Python, SQL, JavaScript
Frameworks: FastAPI, Django, Flask
Databases: PostgreSQL, Redis, MongoDB
Cloud: AWS (EC2, Lambda, RDS, S3, CloudWatch)
Tools: Docker, Kubernetes, Git, CI/CD
"""
    
    print("\n" + "="*80)
    print("STAGE 1: GEMINI CODE EVALUATION + QUESTION GENERATION")
    print("="*80)
    stage1 = pipeline.run_stage1(code_solution)
    
    print("\n" + "="*80)
    print("STAGE 2: QDRANT VECTOR SCORING")
    print("="*80)
    stage2 = pipeline.run_stage2(resume_text)
    
    # Sample video interview transcriptions
    interview_transcripts = [
        "I chose Counter because it provides O(n) time complexity for counting frequencies and has a built-in most_common method that uses a heap internally for efficient top-K selection. This is better than manually sorting which would be O(n log n).",
        
        "For edge cases, I added checks for empty lists and invalid k values at the beginning. In production, I would also add input validation with proper type hints, custom exceptions, and logging for debugging.",
        
        "The space complexity is O(n) for the Counter dictionary which stores all unique elements. If memory is a concern and K is much smaller than N, we could use a min-heap approach to keep only K elements in memory, reducing space to O(K).",
        
        "I would add comprehensive unit tests covering edge cases like empty lists, single elements, duplicates, negative numbers. Also performance tests with large datasets to verify the time complexity, and integration tests for the REST API endpoints.",
        
        "To scale this solution, I would implement Redis caching for frequent queries, add database indexing if we're storing results, use async processing with Celery for large datasets, and consider load balancing with multiple API instances behind a reverse proxy."
    ]
    
    # Sample MCQ answers (correct answers from generated questions)
    mcq_answers = ["B", "A", "C", "B", "A"]
    
    print("\n" + "="*80)
    print("STAGE 3: VIDEO INTERVIEW + MCQ ASSESSMENT")
    print("="*80)
    stage3 = pipeline.run_stage3(interview_transcripts, mcq_answers)
    
    print("\n" + "="*80)
    print("STAGE 4: GEMINI FINAL COMPREHENSIVE ANALYSIS")
    print("="*80)
    stage4 = pipeline.run_stage4()
    
    print("\n" + "="*80)
    print("COMPLETION & QDRANT INDEXING")
    print("="*80)
    final_candidate_id = pipeline.complete()
    
    # Get complete evaluation
    evaluation = pipeline.get_full_evaluation()
    
    # Save to file
    output_file = f"evaluation_{candidate_id}.json"
    with open(output_file, 'w') as f:
        json.dump(evaluation, f, indent=2)
    
    print("\n" + "="*80)
    print("🎉 EVALUATION COMPLETE")
    print("="*80)
    print(f"✅ Candidate ID: {final_candidate_id}")
    print(f"✅ Final Score: {stage4['overall_score']}/100")
    print(f"✅ Recommendation: {stage4['recommendation']}")
    print(f"💾 Saved to: {output_file}")
    
    print("\n📊 SCORE BREAKDOWN:")
    print(f"   Resume Fit:      {stage4['resume_fit_score']}/100")
    print(f"   Code Fit:        {stage4['code_fit_score']}/100")
    print(f"   Code Quality:    {stage4['code_quality_score']}/100")
    print(f"   Video Interview: {stage4['video_interview_score']}/100")
    print(f"   MCQ Score:       {stage4['mcq_score']}/100")
    
    print("\n💪 STRENGTHS:")
    for strength in stage4['strengths']:
        print(f"   • {strength}")
    
    print("\n⚠️  AREAS FOR IMPROVEMENT:")
    for weakness in stage4['weaknesses']:
        print(f"   • {weakness}")
    
    print("\n📝 SUMMARY:")
    print(f"   {stage4['summary']}")
    
    return evaluation

if __name__ == "__main__":
    try:
        results = test_complete_evaluation()
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)