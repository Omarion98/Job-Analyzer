# AI Career Copilot

AI Career Copilot is a full-stack AI application that analyzes how well a candidate's CV matches a job description.

The application extracts text from a PDF resume, compares it against a job description using a locally hosted Large Language Model, and returns a structured match report containing strengths, missing skills, partial matches, interview preparation topics, learning priorities, and an overall match score.

## Features

* Upload a CV as a PDF
* Extract resume text automatically
* Paste and analyze job descriptions
* Compare CV experience against job requirements
* Generate an overall match score
* Identify strong skill matches
* Identify missing skills
* Identify partial matches
* Generate relevant interview preparation topics
* Generate learning priorities
* Generate an overall candidate assessment
* Validate LLM output using Pydantic
* Display results in a responsive React dashboard
* Run the LLM locally using Ollama

## Tech Stack

### Frontend

* React
* TypeScript
* Vite
* CSS
* Fetch API
* FormData

### Backend

* Python
* FastAPI
* Pydantic
* HTTPX
* pypdf
* python-multipart

### AI

* Ollama
* Gemma 3
* Structured LLM outputs
* JSON Schema
* Prompt engineering


## How It Works

### 1. CV Upload

The user uploads a PDF resume through the React frontend.

The frontend sends the PDF and job description to the FastAPI backend using `multipart/form-data`.

### 2. PDF Processing

FastAPI receives the uploaded file and uses `pypdf` to extract its text content.

```text
PDF
 ↓
Binary File
 ↓
pypdf
 ↓
CV Text
```

### 3. CV and Job Analysis

The extracted CV text and job description are included in a structured prompt and sent to a locally running Gemma model through Ollama.

The model compares important requirements from the job description against evidence in the CV.

Requirements are classified into categories such as:

* Strong Match
* Partial Match
* Missing Skill

The model also generates:

* Match score
* Interview topics
* Learning priorities
* Overall candidate assessment

### 4. Structured LLM Output

The application uses structured outputs rather than relying on unrestricted natural-language responses.

The backend supplies a JSON Schema describing the required response structure.

Example:

```json
{
  "match_score": 85,
  "strong_matches": [
    "Python",
    "FastAPI",
    "RAG",
    "Vector Databases",
    "Docker"
  ],
  "missing_skills": [
    "Azure",
    "Kubernetes",
    "CI/CD"
  ],
  "partial_matches": [
    "Machine Learning",
    "Data Engineering"
  ],
  "interview_topics": [
    "RAG Architecture",
    "Vector Databases",
    "LLM Deployment",
    "Prompt Engineering",
    "LLM Monitoring"
  ],
  "learning_priorities": [
    "Azure Cloud Services",
    "Kubernetes",
    "CI/CD Pipelines"
  ],
  "final_assessment": "The candidate demonstrates a strong foundation in AI engineering..."
}
```

### 5. Validation

The LLM response is validated using a Pydantic model before being returned by the API.

```text
Ollama
   ↓
Structured JSON
   ↓
Pydantic Validation
   ↓
FastAPI Response
   ↓
React Dashboard
```

This gives the frontend a predictable API contract instead of requiring it to parse arbitrary LLM-generated text.

### 6. Results Dashboard

The React application displays the structured analysis in separate sections for:

* Overall match score
* Strong matches
* Missing skills
* Partial matches
* Interview preparation topics
* Learning priorities
* Final candidate assessment

## Project Structure

```text
ai-career-copilot/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── pdf_utils.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── home.png
│   └── results.png
│
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

Make sure the following are installed:

* Python 3.11+
* Node.js
* npm
* Ollama
* Git

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ai-career-copilot
```

### 2. Install the Ollama Model

Download Gemma 3:

```bash
ollama pull gemma3:4b
```

Verify the installed models:

```bash
ollama list
```

Make sure Ollama is running before starting the backend.

### 3. Set Up the Backend

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment.

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI development server:

```bash
fastapi dev main.py
```

The backend will be available at:

```text
http://localhost:8000
```

FastAPI interactive documentation:

```text
http://localhost:8000/docs
```

### 4. Set Up the Frontend

Open another terminal and navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

## Usage

1. Start Ollama.
2. Start the FastAPI backend.
3. Start the React frontend.
4. Open the application in your browser.
5. Upload a PDF CV.
6. Paste a job description.
7. Click **Analyze Match**.
8. Review the generated match report.

## API

### Analyze CV Match

```text
POST /api/match
```

The endpoint accepts:

```text
multipart/form-data
```

with:

```text
cv              PDF file
job_description Job description text
```

The API returns a structured response:

```json
{
  "match_score": 85,
  "strong_matches": [],
  "missing_skills": [],
  "partial_matches": [],
  "interview_topics": [],
  "learning_priorities": [],
  "final_assessment": ""
}
```

## Privacy

The current application runs the language model locally through Ollama.

Uploaded CVs are processed by the local FastAPI backend and analyzed by the locally running model. No external LLM API is required.

## License

See the repository license for usage and distribution terms.
