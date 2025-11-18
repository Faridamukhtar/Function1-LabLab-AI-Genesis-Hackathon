import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  async startEvaluation(formData) {
    const data = new FormData()
    data.append('resume', formData.resume)
    data.append('code_solution', formData.codeSolution)
    data.append('job_description', formData.jobDescription)
    data.append('ideal_candidate_profile', formData.idealCandidateProfile)
    data.append('task_description', formData.taskDescription)
    data.append('candidate_id', formData.candidateId)
    data.append('jd_id', formData.jdId)

    const response = await axios.post(`${API_BASE_URL}/api/evaluate/start`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  },

  async completeEvaluation({ evaluationData, recordedVideos, mcqAnswers }) {
    const data = new FormData()
    
    // Use the new /evaluate/complete endpoint that uses stored session data
    data.append('candidate_id', evaluationData.candidate_id)
    data.append('mcq_answers', JSON.stringify(mcqAnswers))
    data.append('human_approved', 'true')

    // Add video files
    recordedVideos.forEach((video, index) => {
      data.append('interview_videos', video, `video_${index}.webm`)
    })

    const response = await axios.post(`${API_BASE_URL}/api/evaluate/complete`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  },
}

