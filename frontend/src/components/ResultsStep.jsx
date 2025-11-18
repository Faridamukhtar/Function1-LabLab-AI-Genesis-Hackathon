import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { CheckCircle, XCircle, TrendingUp, Award } from 'lucide-react'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function ResultsStep({ results }) {
  if (!results) {
    return (
      <div className="bg-white rounded-lg shadow-xl p-8 text-center">
        <p className="text-gray-500">Loading results...</p>
      </div>
    )
  }

  const evaluation = results.evaluation || {}
  const stage4 = evaluation.stage4 || {}
  const stage2 = evaluation.stage2 || {}
  const stage1 = evaluation.stage1 || {}
  const stage3 = evaluation.stage3 || {}

  const scoreData = [
    { name: 'Resume Fit', score: stage4.resume_fit_score || stage2.resume_fit_score || 0 },
    { name: 'Code Fit', score: stage4.code_fit_score || stage2.code_fit_score || 0 },
    { name: 'Code Quality', score: stage4.code_quality_score || stage1.code_quality_score || 0 },
    { name: 'Video Interview', score: stage4.video_interview_score || 0 },
    { name: 'MCQ Score', score: stage4.mcq_score || stage3.mcq_result?.mcq_score || 0 },
  ]

  const overallScore = stage4.overall_score || 0
  const recommendation = stage4.recommendation || 'Pending'

  const getRecommendationColor = (rec) => {
    if (rec.includes('Strong Hire')) return 'text-green-600'
    if (rec.includes('Hire')) return 'text-blue-600'
    if (rec.includes('Maybe')) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-6">
      {/* Overall Score Card */}
      <div className="bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg shadow-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">Final Evaluation Score</h2>
            <p className="text-primary-100">Comprehensive candidate assessment</p>
          </div>
          <div className="text-right">
            <div className="text-6xl font-bold mb-2">{overallScore}</div>
            <div className="text-primary-200">out of 100</div>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      <div className="bg-white rounded-lg shadow-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">Recommendation</h3>
            <p className={`text-2xl font-bold ${getRecommendationColor(recommendation)}`}>
              {recommendation}
            </p>
          </div>
          <Award className="w-12 h-12 text-primary-600" />
        </div>
      </div>

      {/* Score Breakdown Chart */}
      <div className="bg-white rounded-lg shadow-xl p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-6">Score Breakdown</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={scoreData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Bar dataKey="score" fill="#0ea5e9" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {scoreData.map((item, index) => (
          <div key={index} className="bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="text-3xl font-bold text-primary-600 mb-2">{item.score}</div>
            <div className="text-sm text-gray-600">{item.name}</div>
          </div>
        ))}
      </div>

      {/* Summary */}
      {stage4.summary && (
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Summary</h3>
          <p className="text-gray-700 leading-relaxed">{stage4.summary}</p>
        </div>
      )}

      {/* Strengths */}
      {stage4.strengths && stage4.strengths.length > 0 && (
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
            Strengths
          </h3>
          <ul className="space-y-2">
            {stage4.strengths.map((strength, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weaknesses */}
      {stage4.weaknesses && stage4.weaknesses.length > 0 && (
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <XCircle className="w-6 h-6 text-red-600 mr-2" />
            Areas for Improvement
          </h3>
          <ul className="space-y-2">
            {stage4.weaknesses.map((weakness, index) => (
              <li key={index} className="flex items-start">
                <span className="text-red-600 mr-2">•</span>
                <span className="text-gray-700">{weakness}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* MCQ Results */}
      {stage3.mcq_result && (
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">MCQ Assessment</h3>
          <div className="flex items-center space-x-4">
            <div className="text-4xl font-bold text-primary-600">
              {stage3.mcq_result.correct_count}/{stage3.mcq_result.total_count}
            </div>
            <div>
              <div className="text-sm text-gray-600">Correct Answers</div>
              <div className="text-lg font-semibold text-gray-900">
                {stage3.mcq_result.mcq_score}% Score
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

