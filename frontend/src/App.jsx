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
                <span className="text-gray-700">
                  Post positions & coding tasks
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">
                  AI evaluates candidates automatically
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">
                  Review comprehensive candidate reports
                </span>
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
              Browse opportunities, solve challenges, and showcase your skills
              through AI-powered interviews
            </p>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">Browse open positions</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                <span className="text-gray-700">
                  Complete coding challenges
                </span>
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

// COMPANY FLOW (Placeholder)
const CompanyFlow = ({ onBack }) => {
  return (
    <div className="min-h-screen">
      <CompanyNavbar onBack={onBack} />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <Briefcase className="w-16 h-16 text-blue-600 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Company Portal
          </h2>
          <p className="text-gray-600">Company features coming soon...</p>
        </div>
      </div>
    </div>
  );
};

const CompanyNavbar = ({ onBack }) => (
  <nav className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <button onClick={onBack} className="text-gray-600 hover:text-gray-900">
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-blue-600">Company Portal</h1>
      </div>
    </div>
  </nav>
);

// CANDIDATE FLOW
const CandidateFlow = ({ onBack }) => {
  const [step, setStep] = useState("browse");
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [applicationData, setApplicationData] = useState(null);
  const [evaluationResult, setEvaluationResult] = useState(null);

  return (
    <div className="min-h-screen">
      <CandidateNavbar onBack={onBack} />

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
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Browse Opportunities
        </h2>
        <p className="text-gray-600">
          Find your next challenge and showcase your skills
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {positions.map((position) => (
          <div
            key={position.id}
            className="bg-white rounded-xl shadow hover:shadow-xl transition p-6"
          >
            <div className="mb-4">
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {position.title}
              </h3>
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
      <button
        onClick={onBack}
        className="text-purple-600 mb-6 hover:text-purple-700"
      >
        ← Back to Browse
      </button>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            {position.title}
          </h2>

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
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Job Description
            </h3>
            <p className="text-gray-700 leading-relaxed">
              {position.description}
            </p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Requirements
            </h3>
            <p className="text-gray-700">{position.requirements}</p>
          </div>

          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              Coding Challenge
            </h3>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-purple-900 font-semibold mb-2">
                {position.taskDescription}
              </p>
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
      <button
        onClick={onBack}
        className="text-purple-600 mb-6 hover:text-purple-700"
      >
        ← Back
      </button>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Apply to {position.title}
        </h2>
        <p className="text-gray-600 mb-8">
          Step 1 of 3: Submit your application
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
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
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
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
                {resumeFile
                  ? resumeFile.name
                  : "Click to upload or drag and drop"}
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
  const [repoLink, setRepoLink] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const resumeText = await applicationData.resumeFile.text();
      
      const response = await fetch(`http://localhost:8000/api/evaluate/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_link: repoLink,
          job_description: position.description,
          ideal_candidate_profile: position.idealProfile,
          task_description: position.taskDescription,
          candidate_id: applicationData.candidateId,
          jd_id: position.id,
          resume_content: resumeText,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to submit");
      }

      const result = await response.json();
      onNext({
        ...result,
        resumeFile: applicationData.resumeFile
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="bg-red-50 p-4 text-red-700">{error}</div>}
        <input
          type="url"
          required
          value={repoLink}
          onChange={(e) => setRepoLink(e.target.value)}
          placeholder="https://github.com/username/repo"
          className="w-full px-4 py-2 border rounded"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-purple-600 text-white rounded disabled:bg-gray-400"
        >
          {loading ? "Evaluating..." : "Submit Repository →"}
        </button>
      </form>
    </div>
  );
};

const TakeInterview = ({ applicationData, onComplete }) => {
  const [loading, setLoading] = useState(false);
  const [videoBlobs, setVideoBlobs] = useState([]);
  const [mcqAnswers, setMcqAnswers] = useState({});

  const handleSubmit = async () => {
    setLoading(true);
    
    const formData = new FormData();
    formData.append("candidate_id", applicationData.candidate_id);
    
    videoBlobs.forEach((blob, i) => {
      formData.append("interview_videos", blob, `video_${i}.webm`);
    });
    
    formData.append("mcq_answers", JSON.stringify(
      applicationData.mcq_questions.map((_, i) => mcqAnswers[i] || 'A')
    ));

    try {
      const response = await fetch(`http://localhost:8000/api/evaluate/submit-responses`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) throw new Error("Failed to submit");
      
      const result = await response.json();
      onComplete(result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Video recording components */}
      {/* MCQ selection components */}
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="px-4 py-2 bg-green-600 text-white rounded"
      >
        {loading ? "Processing..." : "Submit Responses →"}
      </button>
    </div>
  );
};

export default MicroApprenticeshipPlatform;