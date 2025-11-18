import { useState } from 'react'
import { Upload, FileText, Code, Briefcase, User, Loader2 } from 'lucide-react'
import { api } from '../services/api'

export function UploadStep({ onComplete }) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    resume: null,
    codeSolution: '',
    jobDescription: '',
    idealCandidateProfile: '',
    taskDescription: '',
    candidateId: `candidate_${Date.now()}`,
    jdId: `jd_${Date.now()}`,
  })

  const handleFileChange = (e) => {
    setFormData({ ...formData, resume: e.target.files[0] })
  }

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const data = await api.startEvaluation(formData)
      // Store form data for later use
      data.formData = formData
      onComplete(data)
    } catch (error) {
      alert('Error starting evaluation: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-xl p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Step 1: Upload Resume & Code Solution
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Resume Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <FileText className="inline w-4 h-4 mr-2" />
            Resume (PDF)
          </label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-primary-500 transition-colors">
            <div className="space-y-1 text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="flex text-sm text-gray-600">
                <label className="relative cursor-pointer rounded-md font-medium text-primary-600 hover:text-primary-500">
                  <span>Upload a file</span>
                  <input
                    type="file"
                    className="sr-only"
                    accept=".pdf"
                    onChange={handleFileChange}
                    required
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PDF up to 10MB</p>
              {formData.resume && (
                <p className="text-sm text-green-600 mt-2">
                  ✓ {formData.resume.name}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Code Solution */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Code className="inline w-4 h-4 mr-2" />
            Code Solution
          </label>
          <textarea
            name="codeSolution"
            rows="10"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
            placeholder="Paste your code solution here..."
            value={formData.codeSolution}
            onChange={handleInputChange}
            required
          />
        </div>

        {/* Job Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Briefcase className="inline w-4 h-4 mr-2" />
            Job Description
          </label>
          <textarea
            name="jobDescription"
            rows="4"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Enter the job description..."
            value={formData.jobDescription}
            onChange={handleInputChange}
            required
          />
        </div>

        {/* Ideal Candidate Profile */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <User className="inline w-4 h-4 mr-2" />
            Ideal Candidate Profile
          </label>
          <textarea
            name="idealCandidateProfile"
            rows="3"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Describe the ideal candidate profile..."
            value={formData.idealCandidateProfile}
            onChange={handleInputChange}
            required
          />
        </div>

        {/* Task Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Task Description
          </label>
          <textarea
            name="taskDescription"
            rows="3"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="Describe the coding task..."
            value={formData.taskDescription}
            onChange={handleInputChange}
            required
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary-600 text-white py-3 px-4 rounded-md font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin mr-2" />
              Processing...
            </>
          ) : (
            'Start Evaluation'
          )}
        </button>
      </form>
    </div>
  )
}

