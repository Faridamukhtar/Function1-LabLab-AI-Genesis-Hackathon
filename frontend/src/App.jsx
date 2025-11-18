import React, { useState, useEffect, useRef } from "react";
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
  Play,
  Square,
  Volume2,
  Download,
  Share2,
  Award,
  BarChart3,
} from "lucide-react";

const API_BASE_URL = "http://localhost:8000/api";

// ============ MAIN APP ============
const HackathonSubmission = () => {
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

// ============ LANDING PAGE ============
const LandingPage = ({ onSelectType }) => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-6xl w-full">
        <div className="text-center mb-12">
          <div className="inline-block mb-4">
            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center">
              <Award className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            Holistic Hires
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Holistic, bias-free hiring with AI-powered evaluations and video
            interviews
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Company Card */}
          <div
            onClick={() => onSelectType("company")}
            className="bg-white rounded-2xl shadow-xl p-8 cursor-pointer hover:shadow-2xl transition-all hover:scale-105 group"
          >
            <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-200 transition">
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
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">
                  Post positions & coding tasks
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">
                  AI evaluates candidates automatically
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">
                  Review comprehensive candidate reports
                </span>
              </li>
            </ul>
            <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition">
              Enter as Company
            </button>
          </div>

          {/* Candidate Card */}
          <div
            onClick={() => onSelectType("candidate")}
            className="bg-white rounded-2xl shadow-xl p-8 cursor-pointer hover:shadow-2xl transition-all hover:scale-105 group"
          >
            <div className="w-16 h-16 bg-purple-100 rounded-xl flex items-center justify-center mb-6 group-hover:bg-purple-200 transition">
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
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">Browse open positions</span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700">
                  Complete coding challenges
                </span>
              </li>
              <li className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
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

// ============ COMPANY FLOW ============
const CompanyFlow = ({ onBack }) => {
  return (
    <div className="min-h-screen">
      <CompanyNavbar onBack={onBack} />
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <Briefcase className="w-16 h-16 text-blue-600 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Company Portal
          </h2>
          <p className="text-gray-600 text-lg">
            Company features coming soon in next release...
          </p>
        </div>
      </div>
    </div>
  );
};

const CompanyNavbar = ({ onBack }) => (
  <nav className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <button
          onClick={onBack}
          className="text-gray-600 hover:text-gray-900 flex items-center"
        >
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-blue-600">Company Portal</h1>
      </div>
    </div>
  </nav>
);

// ============ CANDIDATE FLOW ============
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
            setStep("results");
          }}
          onBack={() => setStep("submit-code")}
        />
      )}

      {step === "results" && (
        <ApplicationStatus
          evaluation={evaluationResult}
          onBackToBrowse={() => {
            setStep("browse");
            setSelectedPosition(null);
            setApplicationData(null);
            setEvaluationResult(null);
          }}
        />
      )}
    </div>
  );
};

const CandidateNavbar = ({ onBack }) => (
  <nav className="bg-white shadow-sm border-b">
    <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <button
          onClick={onBack}
          className="text-gray-600 hover:text-gray-900 flex items-center"
        >
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-purple-600">Candidate Portal</h1>
      </div>
    </div>
  </nav>
);

// ============ BROWSE POSITIONS ============
const BrowsePositions = ({ onSelectPosition }) => {
  const [positions, setPositions] = useState([
    {
      id: "1",
      title: "Senior Backend Engineer",
      company: "TechCorp",
      description: "Build scalable microservices with Python and AWS",
      idealProfile:
        "Expert Python developer with 5+ years experience in backend systems",
      taskDescription:
        "Implement a solution to find the Top K Frequent Elements in an array",
      location: "Remote",
      salaryRange: "$120k - $180k",
      requirements: "5+ years Python, AWS, Docker, Kubernetes experience",
      experience: "Senior",
    },
    {
      id: "2",
      title: "Full Stack Developer",
      company: "StartupXYZ",
      description: "Build web applications with React and Node.js",
      idealProfile: "Full stack developer with React and Node.js expertise",
      taskDescription:
        "Create a REST API for a task management system with authentication",
      location: "Remote",
      salaryRange: "$80k - $130k",
      requirements: "3+ years React, Node.js, PostgreSQL experience",
      experience: "Mid-level",
    },
    {
      id: "3",
      title: "Junior Frontend Developer",
      company: "WebStudio",
      description: "Build beautiful user interfaces with React",
      idealProfile:
        "Passionate frontend developer with strong React fundamentals",
      taskDescription:
        "Build a responsive weather application using React and a weather API",
      location: "Remote",
      salaryRange: "$60k - $90k",
      requirements: "1+ years React, HTML, CSS, JavaScript experience",
      experience: "Junior",
    },
  ]);

  const [filteredPositions, setFilteredPositions] = useState(positions);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const filtered = positions.filter(
      (p) =>
        p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredPositions(filtered);
  }, [searchTerm, positions]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="mb-8">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          Browse Opportunities
        </h2>
        <p className="text-gray-600 text-lg">
          Find your next challenge and showcase your skills
        </p>
      </div>

      <div className="mb-8">
        <input
          type="text"
          placeholder="Search positions, companies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
      </div>

      {filteredPositions.length === 0 ? (
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">
            No positions found matching your search
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPositions.map((position) => (
            <div
              key={position.id}
              className="bg-white rounded-xl shadow hover:shadow-xl transition p-6"
            >
              <div className="mb-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">
                      {position.title}
                    </h3>
                    <p className="text-sm text-gray-500">{position.company}</p>
                  </div>
                  <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
                    {position.experience}
                  </span>
                </div>
                <p className="text-gray-600 text-sm line-clamp-2">
                  {position.description}
                </p>
              </div>

              <div className="space-y-2 mb-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <span className="mr-2">📍</span>
                  {position.location}
                </div>
                <div className="flex items-center">
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
      )}
    </div>
  );
};

// ============ POSITION DETAIL ============
const PositionDetail = ({ position, onApply, onBack }) => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button
        onClick={onBack}
        className="text-purple-600 mb-6 hover:text-purple-700 flex items-center font-semibold"
      >
        ← Back to Browse
      </button>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="mb-8">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-2">
                {position.title}
              </h2>
              <p className="text-lg text-gray-600">{position.company}</p>
            </div>
            <span className="text-sm bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
              {position.experience}
            </span>
          </div>

          <div className="flex flex-wrap gap-4 text-gray-600">
            <div className="flex items-center">
              <span className="mr-2">📍</span>
              {position.location}
            </div>
            <div className="flex items-center">
              <span className="mr-2">💰</span>
              {position.salaryRange}
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8 py-8 border-y">
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Timeline</h3>
            <p className="text-gray-600">2-3 weeks</p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Interview Type</h3>
            <p className="text-gray-600">AI Video + MCQ</p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Assessment</h3>
            <p className="text-gray-600">5 questions</p>
          </div>
        </div>

        <div className="space-y-8 mb-8">
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
              <Briefcase className="w-5 h-5 mr-2 text-purple-600" />
              Job Description
            </h3>
            <p className="text-gray-700 leading-relaxed">
              {position.description}
            </p>
          </div>

          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
              <Code className="w-5 h-5 mr-2 text-purple-600" />
              Requirements
            </h3>
            <p className="text-gray-700">{position.requirements}</p>
          </div>

          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-purple-600" />
              Ideal Candidate Profile
            </h3>
            <p className="text-gray-700">{position.idealProfile}</p>
          </div>

          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
              <Code className="w-5 h-5 mr-2 text-purple-600" />
              Coding Challenge
            </h3>
            <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-6">
              <p className="text-purple-900 font-semibold text-lg">
                {position.taskDescription}
              </p>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              How It Works
            </h3>
            <div className="space-y-3">
              <div className="flex items-start">
                <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold mr-3 flex-shrink-0">
                  1
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Upload Resume</p>
                  <p className="text-gray-600">
                    Submit your resume and GitHub repo
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold mr-3 flex-shrink-0">
                  2
                </div>
                <div>
                  <p className="font-semibold text-gray-900">
                    AI Evaluates Code
                  </p>
                  <p className="text-gray-600">
                    Gemini analyzes your code and generates questions
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold mr-3 flex-shrink-0">
                  3
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Video Interview</p>
                  <p className="text-gray-600">
                    Record your responses to AI-generated questions
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold mr-3 flex-shrink-0">
                  4
                </div>
                <div>
                  <p className="font-semibold text-gray-900">Get Results</p>
                  <p className="text-gray-600">
                    Comprehensive AI-generated feedback
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={onBack}
            className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
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

// ============ APPLY FORM ============
const ApplyForm = ({ position, onNext, onBack }) => {
  const [formData, setFormData] = useState({
    candidateId: `CAND_${Date.now()}`,
    name: "",
    email: "",
  });
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && file.type === "application/pdf") {
      setResumeFile(file);
      setError("");
    } else {
      setError("Please select a valid PDF file");
      setResumeFile(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!resumeFile) {
      setError("Please upload a resume");
      return;
    }

    setLoading(true);
    try {
      onNext({
        ...formData,
        resumeFile,
      });
    } catch (err) {
      setError("Failed to submit application");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <button
        onClick={onBack}
        className="text-purple-600 mb-6 hover:text-purple-700 flex items-center font-semibold"
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

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

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
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Upload Resume (PDF) *
            </label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-500 transition cursor-pointer"
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-900 font-semibold mb-1">
                {resumeFile ? (
                  <span className="text-green-600 flex items-center justify-center">
                    <CheckCircle className="w-5 h-5 mr-2" />
                    {resumeFile.name}
                  </span>
                ) : (
                  "Click to upload or drag and drop"
                )}
              </p>
              <p className="text-sm text-gray-500">PDF up to 10MB</p>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900">
              ✓ By applying, you agree to take a video interview and coding
              assessment powered by AI.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 pt-6">
            <button
              type="button"
              onClick={onBack}
              className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={loading || !resumeFile}
              className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                "Submit Application →"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// ============ SUBMIT CODE ============
const SubmitCode = ({ position, applicationData, onNext, onBack }) => {
  const [repoLink, setRepoLink] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // Create FormData to send PDF file
      const formData = new FormData();
      formData.append("repo_link", repoLink);
      formData.append("job_description", position.description);
      formData.append("ideal_candidate_profile", position.idealProfile);
      formData.append("task_description", position.taskDescription);
      formData.append("candidate_id", applicationData.candidateId);
      formData.append("jd_id", position.id);
      formData.append("resume_file", applicationData.resumeFile); // Send PDF directly

      const response = await fetch(`${API_BASE_URL}/evaluate/start`, {
        method: "POST",
        body: formData, // Send as FormData, not JSON
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to submit");
      }

      const result = await response.json();
      onNext({
        ...applicationData,
        ...result,
      });
    } catch (err) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <button
        onClick={onBack}
        className="text-purple-600 mb-6 hover:text-purple-700 flex items-center font-semibold"
      >
        ← Back
      </button>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Task Info */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <Code className="w-6 h-6 mr-2 text-purple-600" />
            Coding Challenge
          </h2>

          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Task</h3>
            <p className="text-gray-700 leading-relaxed mb-4">
              {position.taskDescription}
            </p>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-2">💡 Tips</h4>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>• Push your solution to a GitHub repository</li>
                <li>• Include a README explaining your approach</li>
                <li>• Write clean, well-commented code</li>
                <li>• Test edge cases thoroughly</li>
                <li>• Follow best practices for your language</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Submission Form */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Submit Your Solution
          </h3>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-red-700">{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                GitHub Repository Link *
              </label>
              <input
                type="url"
                required
                value={repoLink}
                onChange={(e) => setRepoLink(e.target.value)}
                placeholder="https://github.com/username/repo"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Example: https://github.com/john/top-k-frequent-elements
              </p>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-sm text-purple-900">
                <span className="font-semibold">Note:</span> Your repository
                will be analyzed by AI to evaluate code quality, functionality,
                and approach.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading || !repoLink}
              className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader className="w-5 h-5 mr-2 animate-spin" />
                  Analyzing Repository...
                </>
              ) : (
                <>
                  <Code className="w-5 h-5 mr-2" />
                  Submit Repository →
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

// ============ TAKE INTERVIEW ============
const TakeInterview = ({ applicationData, onComplete, onBack }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [phase, setPhase] = useState("video");
  const [isRecording, setIsRecording] = useState(false);
  const [videoBlobs, setVideoBlobs] = useState([]);
  const [mcqAnswers, setMcqAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [cameraError, setCameraError] = useState("");

  const createAudioUrl = (audioBase64, mimeType) => {
    if (!audioBase64) return null;
    const byteString = atob(audioBase64);
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uintArray = new Uint8Array(arrayBuffer);

    for (let i = 0; i < byteString.length; i++) {
      uintArray[i] = byteString.charCodeAt(i);
    }

    const blob = new Blob([uintArray], { type: mimeType || "audio/mpeg" });
    return URL.createObjectURL(blob);
  };

  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  const interviewQuestions = applicationData.interview_questions || [];
  const mcqQuestions = applicationData.mcq_questions || [];

  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  // Load audio when question changes
  useEffect(() => {
    const q = interviewQuestions[currentQuestion];
    if (!q?.audio_base64) {
      setAudioUrl(null);
      setIsPlaying(false);
      return;
    }

    // Clean up previous audio URL
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }

    const url = createAudioUrl(q.audio_base64, q.mime_type);
    setAudioUrl(url);
    setIsPlaying(false);

    // Cleanup on unmount
    return () => {
      if (url) {
        URL.revokeObjectURL(url);
      }
    };
  }, [currentQuestion, interviewQuestions]);

  const handlePlayAudio = async () => {
    if (!audioRef.current || !audioUrl) {
      console.log("Audio not ready");
      return;
    }

    try {
      // Stop if currently playing
      if (isPlaying) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        setIsPlaying(false);
        return;
      }

      // Reset and play
      audioRef.current.currentTime = 0;
      await audioRef.current.play();
      setIsPlaying(true);
    } catch (err) {
      console.warn("Audio play error:", err);
      setIsPlaying(false);
    }
  };

  // Handle audio end
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleEnded = () => setIsPlaying(false);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("ended", handleEnded);
    };
  }, []);

  const startRecording = async () => {
    try {
      setCameraError("");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: { echoCancellation: true },
      });

      streamRef.current = stream;
      videoRef.current.srcObject = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "video/webm;codecs=vp9",
      });
      mediaRecorderRef.current = mediaRecorder;

      const chunks = [];
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "video/webm" });
        setVideoBlobs([...videoBlobs, blob]);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime((t) => t + 1);
      }, 1000);
    } catch (err) {
      setCameraError(
        "Camera/microphone access denied. Please check permissions."
      );
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const handleMCQAnswer = (questionIndex, answer) => {
    setMcqAnswers({ ...mcqAnswers, [questionIndex]: answer });
  };

  const handleSubmit = async () => {
    setLoading(true);

    const formData = new FormData();
    formData.append("candidate_id", applicationData.candidate_id);

    videoBlobs.forEach((blob, i) => {
      formData.append("interview_videos", blob, `video_${i}.webm`);
    });

    formData.append(
      "mcq_answers",
      JSON.stringify(mcqQuestions.map((_, i) => mcqAnswers[i] || "A"))
    );

    try {
      const response = await fetch(
        `${API_BASE_URL}/evaluate/submit-responses`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) throw new Error("Failed to submit");

      const result = await response.json();
      onComplete(result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // VIDEO PHASE
  if (phase === "video") {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <button
          onClick={onBack}
          className="text-purple-600 mb-6 hover:text-purple-700 flex items-center font-semibold"
        >
          ← Back
        </button>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
              <Video className="w-8 h-8 mr-2 text-red-600" />
              AI Video Interview
            </h2>
            <p className="text-gray-600">
              Step 2 of 3: Answer interview questions on camera
            </p>
          </div>

          <div className="mb-8 bg-gray-100 rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-96 object-cover bg-black"
            />
          </div>

          {cameraError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-red-700">{cameraError}</span>
            </div>
          )}

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 mb-6">
            <div className="flex items-start space-x-4">
              <Volume2 className="w-6 h-6 text-purple-600 mt-1 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-bold text-purple-900 mb-2">
                  Question {currentQuestion + 1} of {interviewQuestions.length}
                </h3>
                <p className="text-purple-800 text-lg">
                  {interviewQuestions[currentQuestion]}
                </p>
                {audioUrl && (
                  <div className="mt-4 flex items-center space-x-4">
                    <button
                      onClick={handlePlayAudio}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition flex items-center"
                    >
                      {isPlaying ? (
                        <>
                          <Square className="w-5 h-5 mr-2" />
                          Stop Audio
                        </>
                      ) : (
                        <>
                          <Volume2 className="w-5 h-5 mr-2" />
                          Play AI Audio
                        </>
                      )}
                    </button>
                    <audio ref={audioRef} src={audioUrl} preload="auto" />
                  </div>
                )}
              </div>
            </div>
          </div>

          {isRecording && (
            <div className="mb-6 flex items-center justify-between bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse mr-2" />
                <span className="font-semibold text-red-900">Recording...</span>
              </div>
              <span className="font-mono text-red-900">
                {formatTime(recordingTime)}
              </span>
            </div>
          )}

          <div className="flex gap-4 mb-6">
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition flex items-center justify-center"
              >
                <Play className="w-5 h-5 mr-2" />
                Start Recording
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="flex-1 px-4 py-3 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition flex items-center justify-center"
              >
                <Square className="w-5 h-5 mr-2" />
                Stop Recording
              </button>
            )}
          </div>

          <button
            onClick={() => {
              if (currentQuestion === interviewQuestions.length - 1) {
                setPhase("mcq");
              } else {
                setCurrentQuestion(currentQuestion + 1);
                setRecordingTime(0);
              }
            }}
            disabled={!videoBlobs[currentQuestion] || isRecording}
            className="w-full px-4 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {currentQuestion === interviewQuestions.length - 1
              ? "Move to MCQ Assessment →"
              : "Next Question →"}
          </button>

          {videoBlobs[currentQuestion] &&
            applicationData?.interview_transcripts?.[currentQuestion] && (
              <div className="bg-gray-100 border border-gray-200 rounded-lg p-4 mt-4">
                <h4 className="font-semibold text-gray-900 mb-2">
                  Transcript Preview
                </h4>
                <p className="text-gray-700">
                  {
                    applicationData.interview_transcripts[currentQuestion]
                      .transcription
                  }
                </p>
              </div>
            )}
        </div>
      </div>
    );
  }

  // MCQ PHASE
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <button
        onClick={onBack}
        className="text-purple-600 mb-6 hover:text-purple-700 flex items-center font-semibold"
      >
        ← Back
      </button>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
            <Code className="w-8 h-8 mr-2 text-blue-600" />
            Coding Assessment
          </h2>
          <p className="text-gray-600">
            Step 3 of 3: Complete multiple choice questions
          </p>
        </div>

        <div className="space-y-6 mb-8">
          {mcqQuestions.map((q, i) => (
            <div
              key={i}
              className="bg-gray-50 border border-gray-200 rounded-lg p-6"
            >
              <h4 className="font-bold text-gray-900 mb-4">
                <span className="bg-purple-600 text-white w-8 h-8 rounded-full inline-flex items-center justify-center mr-3">
                  {i + 1}
                </span>
                {q.question}
              </h4>
              <div className="space-y-2 ml-11">
                {q.options.map((option, optIdx) => {
                  const letter = String.fromCharCode(65 + optIdx);
                  const isSelected = mcqAnswers[i] === letter;
                  return (
                    <label
                      key={optIdx}
                      className={`flex items-center p-3 rounded-lg cursor-pointer transition ${
                        isSelected
                          ? "bg-purple-100 border-2 border-purple-600"
                          : "hover:bg-gray-100 border-2 border-transparent"
                      }`}
                    >
                      <input
                        type="radio"
                        name={`question-${i}`}
                        value={letter}
                        checked={isSelected}
                        onChange={(e) => handleMCQAnswer(i, e.target.value)}
                        className="mr-3"
                      />
                      <span className="font-semibold text-gray-700 mr-2">
                        {letter}.
                      </span>
                      <span className="text-gray-700">{option}</span>
                    </label>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleSubmit}
          disabled={
            loading || Object.keys(mcqAnswers).length < mcqQuestions.length
          }
          className="w-full px-4 py-4 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center text-lg"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 mr-2 animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              <CheckCircle className="w-5 h-5 mr-2" />
              Submit Assessment & Get Results
            </>
          )}
        </button>
      </div>
    </div>
  );
};

// ============ APPLICATION STATUS / RESULTS ============
const ApplicationStatus = ({ evaluation, onBackToBrowse }) => {
  const scores = evaluation.scores || {};
  const overallScore = evaluation.overall_score || 0;

  const getRecommendationColor = (score) => {
    if (score >= 90) return "bg-green-50 border-green-200 text-green-900";
    if (score >= 75) return "bg-blue-50 border-blue-200 text-blue-900";
    if (score >= 60) return "bg-yellow-50 border-yellow-200 text-yellow-900";
    return "bg-red-50 border-red-200 text-red-900";
  };

  const getRecommendationIcon = (score) => {
    if (score >= 90) return <CheckCircle className="w-8 h-8 text-green-600" />;
    if (score >= 75) return <CheckCircle className="w-8 h-8 text-blue-600" />;
    if (score >= 60) return <Clock className="w-8 h-8 text-yellow-600" />;
    return <XCircle className="w-8 h-8 text-red-600" />;
  };

  const getRecommendationText = (score) => {
    if (score >= 90) return "Strong Hire 🎉";
    if (score >= 75) return "Hire ✓";
    if (score >= 60) return "Maybe 🤔";
    return "No Hire";
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-12 text-center">
          <div className="flex justify-center mb-4">
            {getRecommendationIcon(overallScore)}
          </div>
          <h2 className="text-4xl font-bold mb-2">Evaluation Complete!</h2>
          <p className="text-purple-100">
            Your AI-powered assessment results are ready
          </p>
        </div>

        <div className="p-12">
          {/* Overall Score */}
          <div
            className={`border-2 rounded-xl p-8 mb-12 text-center ${getRecommendationColor(
              overallScore
            )}`}
          >
            <div className="text-6xl font-bold mb-2">{overallScore}</div>
            <div className="text-2xl font-semibold mb-2">Overall Score</div>
            <div className="text-lg">{getRecommendationText(overallScore)}</div>
          </div>

          {/* Score Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4 mb-12">
            {[
              { label: "Code Quality", value: scores.code_quality, icon: "💻" },
              { label: "Resume Fit", value: scores.resume_fit, icon: "📄" },
              { label: "Code Fit", value: scores.code_fit, icon: "✔️" },
              { label: "MCQ", value: scores.mcq, icon: "📝" },
              { label: "Interview", value: scores.video_interview, icon: "🎤" },
            ].map((item, i) => (
              <div key={i} className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-3xl mb-2">{item.icon}</div>
                <div className="text-sm text-gray-600 mb-1">{item.label}</div>
                <div className="text-2xl font-bold text-gray-900">
                  {item.value || 0}
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          {evaluation.summary && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
              <h3 className="font-bold text-gray-900 mb-3 flex items-center">
                <BarChart3 className="w-5 h-5 mr-2 text-blue-600" />
                Summary
              </h3>
              <p className="text-gray-700 leading-relaxed">
                {evaluation.summary}
              </p>
            </div>
          )}

          {/* Strengths */}
          {evaluation.strengths && evaluation.strengths.length > 0 && (
            <div className="mb-8">
              <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                Strengths
              </h3>
              <div className="space-y-2">
                {evaluation.strengths.map((strength, i) => (
                  <div
                    key={i}
                    className="flex items-start p-3 bg-green-50 rounded-lg"
                  >
                    <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{strength}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Weaknesses */}
          {evaluation.weaknesses && evaluation.weaknesses.length > 0 && (
            <div className="mb-8">
              <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2 text-yellow-600" />
                Areas for Improvement
              </h3>
              <div className="space-y-2">
                {evaluation.weaknesses.map((weakness, i) => (
                  <div
                    key={i}
                    className="flex items-start p-3 bg-yellow-50 rounded-lg"
                  >
                    <AlertCircle className="w-5 h-5 text-yellow-600 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{weakness}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Interview Transcript Section */}
          {evaluation.interview_transcripts &&
            evaluation.interview_transcripts.length > 0 && (
              <div className="mb-12">
                <h3 className="font-bold text-gray-900 mb-4 flex items-center">
                  <Video className="w-5 h-5 mr-2 text-red-600" />
                  Video Interview Transcripts
                </h3>

                <div className="space-y-4">
                  {evaluation.interview_transcripts.map((item, index) => (
                    <div
                      key={index}
                      className="bg-gray-50 border border-gray-200 p-4 rounded-lg"
                    >
                      <p className="font-semibold text-gray-900 mb-2">
                        Question {index + 1}
                      </p>

                      <p className="text-gray-700 mb-2">
                        <span className="font-semibold text-purple-700">
                          Q:{" "}
                        </span>
                        {item.question}
                      </p>

                      <p className="text-gray-700">
                        <span className="font-semibold text-green-700">
                          Transcript:{" "}
                        </span>
                        {item.transcription}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={onBackToBrowse}
              className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition flex items-center justify-center"
            >
              <TrendingUp className="w-5 h-5 mr-2" />
              Browse More Opportunities
            </button>
            <button className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition flex items-center justify-center">
              <Download className="w-5 h-5 mr-2" />
              Download Report
            </button>
            <button className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition flex items-center justify-center">
              <Share2 className="w-5 h-5 mr-2" />
              Share Results
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HackathonSubmission;
