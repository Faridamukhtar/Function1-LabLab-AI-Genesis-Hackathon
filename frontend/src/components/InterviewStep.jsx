import { useState, useRef, useEffect } from 'react'
import { Video, Mic, CheckCircle, Loader2, Play } from 'lucide-react'
import { api } from '../services/api'

export function InterviewStep({ evaluationData, onComplete }) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [recordedVideos, setRecordedVideos] = useState([])
  const [mcqAnswers, setMcqAnswers] = useState({})
  const [processing, setProcessing] = useState(false)
  const videoRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const interviewQuestions = evaluationData?.interview_questions || []
  const mcqQuestions = evaluationData?.mcq_questions || []

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop()
      }
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })

      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' })
        setRecordedVideos([...recordedVideos, blob])
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      alert('Error accessing camera: ' + error.message)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < interviewQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    }
  }

  const handleMcqAnswer = (questionIndex, answer) => {
    setMcqAnswers({ ...mcqAnswers, [questionIndex]: answer })
  }

  const handleSubmit = async () => {
    if (recordedVideos.length !== interviewQuestions.length) {
      alert('Please record videos for all interview questions')
      return
    }

    if (Object.keys(mcqAnswers).length !== mcqQuestions.length) {
      alert('Please answer all MCQ questions')
      return
    }

    setProcessing(true)

    try {
      const results = await api.completeEvaluation({
        evaluationData: {
          candidate_id: evaluationData?.candidate_id || evaluationData?.formData?.candidateId,
          ...evaluationData
        },
        recordedVideos,
        mcqAnswers: Object.values(mcqAnswers),
      })
      onComplete({ results })
    } catch (error) {
      alert('Error completing evaluation: ' + error.message)
    } finally {
      setProcessing(false)
    }
  }

  const allVideosRecorded = recordedVideos.length === interviewQuestions.length
  const allMcqAnswered = Object.keys(mcqAnswers).length === mcqQuestions.length

  return (
    <div className="space-y-6">
      {/* Video Interview Section */}
      <div className="bg-white rounded-lg shadow-xl p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Step 2: Video Interview
        </h2>

        {interviewQuestions.length > 0 ? (
          <div className="space-y-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-800 mb-2">
                Question {currentQuestionIndex + 1} of {interviewQuestions.length}
              </p>
              <p className="text-lg font-semibold text-gray-900">
                {interviewQuestions[currentQuestionIndex]}
              </p>
            </div>

            <div className="relative bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                muted
                className="w-full h-64 object-cover"
              />
              {isRecording && (
                <div className="absolute top-4 left-4 flex items-center space-x-2 bg-red-600 text-white px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                  <span className="text-sm font-medium">Recording</span>
                </div>
              )}
            </div>

            <div className="flex space-x-4">
              {!isRecording && !recordedVideos[currentQuestionIndex] && (
                <button
                  onClick={startRecording}
                  className="flex-1 bg-red-600 text-white py-3 px-4 rounded-md font-semibold hover:bg-red-700 transition-colors flex items-center justify-center"
                >
                  <Video className="mr-2" />
                  Start Recording
                </button>
              )}

              {isRecording && (
                <button
                  onClick={stopRecording}
                  className="flex-1 bg-gray-600 text-white py-3 px-4 rounded-md font-semibold hover:bg-gray-700 transition-colors"
                >
                  Stop Recording
                </button>
              )}

              {recordedVideos[currentQuestionIndex] && (
                <div className="flex-1 flex items-center justify-center text-green-600">
                  <CheckCircle className="mr-2" />
                  Video Recorded
                </div>
              )}

              {currentQuestionIndex < interviewQuestions.length - 1 && (
                <button
                  onClick={handleNextQuestion}
                  disabled={!recordedVideos[currentQuestionIndex]}
                  className="flex-1 bg-primary-600 text-white py-3 px-4 rounded-md font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next Question
                </button>
              )}
            </div>
          </div>
        ) : (
          <p className="text-gray-500">Loading questions...</p>
        )}
      </div>

      {/* MCQ Section */}
      <div className="bg-white rounded-lg shadow-xl p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Multiple Choice Questions
        </h2>

        <div className="space-y-6">
          {mcqQuestions.map((question, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <p className="font-semibold text-gray-900 mb-3">
                {index + 1}. {question.question}
              </p>
              <div className="space-y-2">
                {question.options.map((option, optIndex) => {
                  const optionLetter = String.fromCharCode(65 + optIndex) // A, B, C, D
                  const isSelected = mcqAnswers[index] === optionLetter
                  
                  return (
                    <label
                      key={optIndex}
                      className={`flex items-center p-3 rounded-md cursor-pointer transition-colors ${
                        isSelected
                          ? 'bg-primary-100 border-2 border-primary-500'
                          : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                      }`}
                    >
                      <input
                        type="radio"
                        name={`mcq-${index}`}
                        value={optionLetter}
                        checked={isSelected}
                        onChange={() => handleMcqAnswer(index, optionLetter)}
                        className="mr-3"
                      />
                      <span className="font-medium mr-2">{optionLetter}.</span>
                      <span>{option}</span>
                    </label>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={!allVideosRecorded || !allMcqAnswered || processing}
        className="w-full bg-green-600 text-white py-4 px-6 rounded-md font-semibold text-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {processing ? (
          <>
            <Loader2 className="animate-spin mr-2" />
            Processing Evaluation...
          </>
        ) : (
          'Submit Evaluation'
        )}
      </button>
    </div>
  )
}

