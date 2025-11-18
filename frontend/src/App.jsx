import React, { useState, useEffect } from "react";
import {
  Upload,
  Code,
  Video,
  CheckCircle,
  XCircle,
  Clock,
  Briefcase,
  Users,
  TrendingUp,
  Loader,
  AlertCircle,
} from "lucide-react";

// API Configuration
const API_BASE_URL = "http://localhost:8000/api";

// Main App Component
const MicroApprenticeshipPlatform = () => {
  const [userType, setUserType] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {!userType ? (
        <LandingPage onSelectType={setUserType} />
      ) : userType === "company" ? (
        <CompanyFlow onBack={() => setUserType(null)} />
      ) : (
        <CandidateFlow onBack={() => setUserType(null)} />
      )}
    </div>
  );
};

// Landing Page
const LandingPage = ({ onSelectType }) => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-6xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI Micro-Apprenticeship Platform
          </h1>
          <p className="text-xl text-gray-600">
            Revolutionizing hiring with AI-powered evaluations
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div
            onClick={() => onSelectType("company")}
            className="bg-white rounded-2xl shadow-xl p-8 cursor-pointer hover:shadow-2xl transition-all hover:scale-105"
          >
            <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mb-6">
              <Briefcase className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              For Companies
            </h2>
            <p className="text-gray-600 mb-6">
              Create positions, design coding challenges, and find top talent
              with AI-assisted evaluation
            </p>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">Post positions & coding tasks</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">AI evaluates candidates automatically</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">Review comprehensive candidate reports</span>
              </li>
            </ul>
            <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
              Enter as Company
            </button>
          </div>

          <div
            onClick={() => onSelectType("candidate")}
            className="bg-white rounded-2xl shadow-xl p-8 cursor-pointer hover:shadow-2xl transition-all hover:scale-105"
          >
            <div className="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center mb-6">
              <Users className="w-8 h-8 text-purple-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              For Candidates
            </h2>
            <p className="text-gray-600 mb-6">
              Browse opportunities, solve challenges, and showcase your skills through AI-powered interviews
            </p>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">Browse open positions</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">Complete coding challenges</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">Take AI video interviews</span>
              </li>
            </ul>
            <button className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition">
              Enter as Candidate
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// COMPANY FLOW
const CompanyFlow = ({ onBack }) => {
  const [step, setStep] = useState("dashboard");
  const [positions, setPositions] = useState([]);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  return (
    <div className="min-h-screen">
      <CompanyNavbar onBack={onBack} />

      {step === "browse" && (
        <BrowsePositions
          onSelectPosition={(position) => {
            setSelectedPosition(position);
            setStep("position-detail");
          }}
        />
      )}

      {step === "position-detail" && (
        <PositionDetail
          position={selectedPosition}
          onApply={() => setStep("apply")}
          onBack={() => setStep("browse")}
        />
      )}

      {step === "apply" && (
        <ApplyForm
          position={selectedPosition}
          onNext={(data) => {
            setApplicationData(data);
            setStep("submit-code");
          }}
          onBack={() => setStep("position-detail")}
        />
      )}

      {step === "submit-code" && (
        <SubmitCode
          position={selectedPosition}
          applicationData={applicationData}
          onNext={(data) => {
            setApplicationData({ ...applicationData, ...data });
            setStep("interview");
          }}
          onBack={() => setStep("apply")}
        />
      )}

      {step === "interview" && (
        <TakeInterview
          applicationData={applicationData}
          onComplete={(result) => {
            setEvaluationResult(result);
            setStep("status");
          }}
        />
      )}

      {step === "status" && (
        <ApplicationStatus
          evaluation={evaluationResult}
          onBackToBrowse={() => setStep("browse")}
        />
      )}
    </div>
  );
};

const CandidateNavbar = ({ onBack }) => (
  <nav className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <button onClick={onBack} className="text-gray-600 hover:text-gray-900">
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-purple-600">Candidate Portal</h1>
      </div>
    </div>
  </nav>
);

const BrowsePositions = ({ onSelectPosition }) => {
  const [positions, setPositions] = useState([
    {
      id: "1",
      title: "Senior Backend Engineer",
      description: "Build scalable microservices",
      idealProfile: "Expert Python developer with 5+ years experience",
      taskDescription: "Build a REST API for Top K Frequent Elements",
      location: "Remote",
      salaryRange: "$120k - $180k",
      requirements: "5+ years Python, AWS experience",
    },
  ]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Browse Opportunities</h2>
        <p className="text-gray-600">Find your next challenge and showcase your skills</p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {positions.map((position) => (
          <div key={position.id} className="bg-white rounded-xl shadow hover:shadow-xl transition p-6">
            <div className="mb-4">
              <h3 className="text-xl font-bold text-gray-900 mb-2">{position.title}</h3>
              <p className="text-gray-600 text-sm">{position.description}</p>
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex items-center text-sm text-gray-600">
                <span className="mr-2">📍</span>
                {position.location}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <span className="mr-2">💰</span>
                {position.salaryRange}
              </div>
            </div>

            <button
              onClick={() => onSelectPosition(position)}
              className="w-full bg-purple-600 text-white py-2 rounded-lg font-semibold hover:bg-purple-700 transition"
            >
              View Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

const PositionDetail = ({ position, onApply, onBack }) => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button onClick={onBack} className="text-purple-600 mb-6 hover:text-purple-700">
        ← Back to Browse
      </button>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">{position.title}</h2>

          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex items-center text-gray-600">
              <span className="mr-2">📍</span>
              {position.location}
            </div>
            <div className="flex items-center text-gray-600">
              <span className="mr-2">💰</span>
              {position.salaryRange}
            </div>
          </div>
        </div>

        <div className="space-y-6 mb-8">
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Job Description</h3>
            <p className="text-gray-700 leading-relaxed">{position.description}</p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Requirements</h3>
            <p className="text-gray-700">{position.requirements}</p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Coding Challenge</h3>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-purple-900 font-semibold mb-2">{position.taskDescription}</p>
            </div>
          </div>
        </div>

        <div className="flex space-x-4">
          <button
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
          >
            Back
          </button>
          <button
            onClick={onApply}
            className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
          >
            Apply Now
          </button>
        </div>
      </div>
    </div>
  );
};

const ApplyForm = ({ position, onNext, onBack }) => {
  const [formData, setFormData] = useState({
    candidateId: `CAND_${Date.now()}`,
    name: "",
    email: "",
  });
  const [resumeFile, setResumeFile] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    onNext({
      ...formData,
      resumeFile,
      position,
    });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button onClick={onBack} className="text-purple-600 mb-6 hover:text-purple-700">
        ← Back
      </button>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Apply to {position.title}</h2>
        <p className="text-gray-600 mb-8">Step 1 of 3: Submit your application</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="john@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Upload Resume (PDF) *
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-500 transition">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                {resumeFile ? resumeFile.name : "Click to upload or drag and drop"}
              </p>
              <p className="text-sm text-gray-500">PDF up to 10MB</p>
              <input
                type="file"
                accept=".pdf"
                required
                onChange={(e) => setResumeFile(e.target.files[0])}
                className="hidden"
                id="resume-upload"
              />
              <label
                htmlFor="resume-upload"
                className="inline-block mt-4 px-4 py-2 bg-purple-100 text-purple-700 rounded-lg cursor-pointer hover:bg-purple-200 transition"
              >
                Choose File
              </label>
            </div>
          </div>

          <div className="flex justify-end space-x-4 pt-6">
            <button
              type="button"
              onClick={onBack}
              className="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
            >
              Back
            </button>
            <button
              type="submit"
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
            >
              Submit & Continue →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const SubmitCode = ({ position, applicationData, onNext, onBack }) => {
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("resume", applicationData.resumeFile);
      formData.append("code_solution", code);
      formData.append("job_description", position.description);
      formData.append("ideal_candidate_profile", position.idealProfile);
      formData.append("task_description", position.taskDescription);
      formData.append("candidate_id", applicationData.candidateId);
      formData.append("jd_id", position.id);

      const response = await fetch(`${API_BASE_URL}/evaluate/start`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to submit code");
      }

      const result = await response.json();
      onNext({
        code,
        interviewQuestions: result.interview_questions,
        mcqQuestions: result.mcq_questions,
        initialScores: result.scores_so_far,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <button onClick={onBack} className="text-purple-600 mb-6 hover:text-purple-700">
        ← Back
      </button>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Coding Challenge</h2>

          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-2">Task</h3>
            <p className="text-gray-700 leading-relaxed mb-4">{position.taskDescription}</p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">💡 Tips</h4>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>• Focus on correctness first</li>
                <li>• Write clean, readable code</li>
                <li>• Add comments for complex logic</li>
                <li>• Test edge cases</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Your Solution</h3>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Code *
              </label>
              <textarea
                required
                rows={16}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="# Your code here"
              />
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  "Submit Solution →"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

const TakeInterview = ({ applicationData, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [videoFiles, setVideoFiles] = useState([]);
  const [showMCQ, setShowMCQ] = useState(false);
  const [mcqAnswers, setMcqAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const questions = applicationData.interviewQuestions || [];
  const mcqQuestions = applicationData.mcqQuestions || [];

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowMCQ(true);
    }
  };

  const handleSubmitInterview = async () => {
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("candidate_id", applicationData.candidateId);
      
      videoFiles.forEach((file) => {
        formData.append("interview_videos", file);
      });

      const answersArray = mcqQuestions.map((q) => mcqAnswers[q.question] || "A");
      formData.append("mcq_answers", JSON.stringify(answersArray));

      const response = await fetch(`${API_BASE_URL}/evaluate/complete`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to complete evaluation");
      }

      const result = await response.json();
      onComplete(result.evaluation);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (showMCQ) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Multiple Choice Assessment</h2>
          <p className="text-gray-600 mb-8">Answer all questions based on your code submission</p>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          )}

          <div className="space-y-8">
            {mcqQuestions.map((q, idx) => (
              <div key={idx} className="pb-6 border-b border-gray-200 last:border-0">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {idx + 1}. {q.question}
                </h3>
                <div className="space-y-2">
                  {q.options.map((option, optIdx) => (
                    <label
                      key={optIdx}
                      className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-purple-50 transition"
                    >
                      <input
                        type="radio"
                        name={`mcq-${idx}`}
                        value={String.fromCharCode(65 + optIdx)}
                        checked={mcqAnswers[q.question] === String.fromCharCode(65 + optIdx)}
                        onChange={(e) =>
                          setMcqAnswers({ ...mcqAnswers, [q.question]: e.target.value })
                        }
                        className="mr-3"
                      />
                      <span className="text-gray-700">
                        {String.fromCharCode(65 + optIdx)}. {option}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleSubmitInterview}
            disabled={loading || Object.keys(mcqAnswers).length < mcqQuestions.length}
            className="w-full mt-8 px-6 py-4 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader className="w-5 h-5 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              "Submit Assessment"
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-3xl font-bold text-gray-900">AI Video Interview</h2>
            <span className="text-sm text-gray-600">
              Question {currentQuestion + 1} of {questions.length}
            </span>
          </div>
          <p className="text-gray-600">Answer questions about your code submission</p>
        </div>

        <div className="mb-8">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all"
              style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        <div className="mb-8 p-6 bg-purple-50 border border-purple-200 rounded-xl">
          <div className="flex items-start mb-4">
            <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
              AI
            </div>
            <div className="flex-1">
              <p className="text-sm text-purple-600 font-semibold mb-2">AI Interviewer asks:</p>
              <p className="text-xl text-gray-900 font-semibold">{questions[currentQuestion]}</p>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <div className="aspect-video bg-gray-900 rounded-xl flex flex-col items-center justify-center relative">
            {isRecording ? (
              <>
                <div className="absolute top-4 right-4 flex items-center space-x-2 bg-red-600 text-white px-3 py-1 rounded-full">
                  <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
                  <span className="text-sm font-semibold">Recording</span>
                </div>
                <Video className="w-24 h-24 text-white mb-4" />
                <p className="text-white">Recording your response...</p>
              </>
            ) : (
              <>
                <Video className="w-24 h-24 text-gray-600 mb-4" />
                <p className="text-gray-400">Click start to record your answer</p>
              </>
            )}
          </div>
        </div>

        <div className="flex space-x-4">
          {!isRecording ? (
            <button
              onClick={() => setIsRecording(true)}
              className="flex-1 px-6 py-4 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition flex items-center justify-center"
            >
              <Video className="w-5 h-5 mr-2" />
              Start Recording
            </button>
          ) : (
            <button
              onClick={() => {
                setIsRecording(false);
                handleNextQuestion();
              }}
              className="flex-1 px-6 py-4 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition"
            >
              Stop & Continue
            </button>
          )}
        </div>

        <button
          onClick={handleNextQuestion}
          className="w-full mt-4 px-6 py-2 text-gray-600 hover:text-gray-900 text-sm"
        >
          Skip this question →
        </button>
      </div>
    </div>
  );
};

const ApplicationStatus = ({ evaluation, onBackToBrowse }) => {
  if (!evaluation || !evaluation.stage4) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <Loader className="w-16 h-16 mx-auto mb-4 animate-spin text-purple-600" />
          <p className="text-gray-600">Processing your evaluation...</p>
        </div>
      </div>
    );
  }

  const stage4 = evaluation.stage4;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Application Submitted!</h2>
          <p className="text-gray-600">
            Your evaluation is complete. The company will review your application soon.
          </p>
        </div>

        <div className="mb-8 p-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border border-purple-200">
          <div className="text-center mb-6">
            <p className="text-gray-600 mb-2">Your Overall Score</p>
            <div className="text-6xl font-bold text-purple-600">{stage4.overall_score}</div>
            <p className="text-xl font-semibold text-gray-700 mt-2">{stage4.recommendation}</p>
          </div>

          <div className="grid grid-cols-5 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-600 mb-1">Resume Fit</p>
              <p className="text-2xl font-bold text-gray-900">{stage4.resume_fit_score}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Code Fit</p>
              <p className="text-2xl font-bold text-gray-900">{stage4.code_fit_score}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Code Quality</p>
              <p className="text-2xl font-bold text-gray-900">{stage4.code_quality_score}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">Interview</p>
              <p className="text-2xl font-bold text-gray-900">{stage4.video_interview_score}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 mb-1">MCQ</p>
              <p className="text-2xl font-bold text-gray-900">{stage4.mcq_score}</p>
            </div>
          </div>
        </div>

        <div className="mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Summary</h3>
          <p className="text-gray-700 leading-relaxed">{stage4.summary}</p>
        </div>

        <div className="space-y-3">
          <button
            onClick={onBackToBrowse}
            className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
          >
            Browse More Positions
          </button>
        </div>
      </div>
    </div>
  );
};

export default MicroApprenticeshipPlatform;