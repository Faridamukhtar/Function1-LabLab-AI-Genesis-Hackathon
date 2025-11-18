# Frontend - AI Candidate Evaluation System

Modern React frontend for the AI Candidate Evaluation System.

## Features

- 📄 Resume upload (PDF)
- 💻 Code solution input
- 🎥 Video interview recording
- 📝 MCQ questions interface
- 📊 Results visualization with charts
- 🎨 Modern, responsive UI

## Setup

### Prerequisites
- Node.js 18+ and npm/yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will run on `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── UploadStep.jsx      # Resume & code upload
│   │   ├── InterviewStep.jsx    # Video interview & MCQ
│   │   └── ResultsStep.jsx      # Results visualization
│   ├── services/
│   │   └── api.js               # API integration
│   ├── App.jsx                  # Main app component
│   ├── main.jsx                 # Entry point
│   └── index.css                # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Usage

1. **Upload Step**: Upload resume PDF and enter code solution
2. **Interview Step**: Record video responses and answer MCQ questions
3. **Results Step**: View comprehensive evaluation results

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`.

Make sure the backend is running before starting the frontend.

