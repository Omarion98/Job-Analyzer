import { useRef, useState } from "react";
import "./App.css";

interface MatchAnalysis {
  match_score: number;

  strong_matches: string[];

  missing_skills: string[];

  partial_matches: string[];

  interview_topics: string[];

  learning_priorities: string[];

  final_assessment: string;
}

interface ErrorResponse {
  detail: string;
}

type ResultType =
  | "positive"
  | "warning"
  | "neutral";


interface ResultCardProps {
  title: string;
  subtitle: string;
  icon: string;
  items: string[];
  type: ResultType;
}


function ResultCard({
  title,
  subtitle,
  icon,
  items,
  type,
}: ResultCardProps) {
  return (
    <div className={`result-card ${type}`}>
      <div className="result-card-header">

        <div className="result-card-title-group">
          <div className="card-icon">
            {icon}
          </div>

          <div>
            <h3>{title}</h3>
            <p>{subtitle}</p>
          </div>
        </div>

        <span className="item-count">
          {items.length}
        </span>

      </div>


      <div className="skill-list">

        {items.length > 0 ? (

          items.map((item, index) => (

            <div
              className="skill-item"
              key={`${item}-${index}`}
            >
              <span className="skill-marker">
                {icon}
              </span>

              <span>
                {item}
              </span>
            </div>

          ))

        ) : (

          <div className="empty-state">
            None identified
          </div>

        )}

      </div>
    </div>
  );
}

interface ScoreCardProps {
  score: number;
  assessment: string;
}


function ScoreCard({
  score,
  assessment,
}: ScoreCardProps) {

  let label = "Needs Improvement";
  let level = "low";

  if (score >= 80) {
    label = "Strong Match";
    level = "high";
  } else if (score >= 60) {
    label = "Good Match";
    level = "medium";
  }


  return (
    <div className="score-card">

      <div
        className={`score-ring ${level}`}
        style={{
          background: `
            conic-gradient(
              currentColor ${score * 3.6}deg,
              #edf0f6 0deg
            )
          `,
        }}
      >
        <div className="score-ring-inner">

          <strong>
            {score}
          </strong>

          <span>
            /100
          </span>

        </div>
      </div>


      <div className="score-content">

        <span className="score-label">
          OVERALL MATCH
        </span>

        <div className="score-heading">

          <h3>
            {label}
          </h3>

          <span
            className={`match-badge ${level}`}
          >
            {score}%
          </span>

        </div>

        <p>
          {assessment}
        </p>

      </div>

    </div>
  );
}

function App() {
  const [cv, setCv] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] =
  useState<MatchAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);

  const selectFile = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Please upload a PDF file.");
      return;
    }

    setCv(file);
    setError("");
  };

  const removeFile = () => {
    setCv(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const analyzeMatch = async () => {
    if (!cv) {
      setError("Please upload your CV.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please paste a job description.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const formData = new FormData();

      formData.append("cv", cv);
      formData.append(
        "job_description",
        jobDescription
      );

      const response = await fetch(
        "http://localhost:8000/api/match",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData: ErrorResponse =
          await response.json();

        throw new Error(
          errorData.detail ||
            "Something went wrong."
        );
      }

      const data: MatchAnalysis  =
        await response.json();

      setAnalysis(data);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError(
          "Could not connect to the backend."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <span>AI Career Copilot</span>
        </div>

        <div className="status">
          <span className="status-dot" />
          Local AI
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="hero-badge">
            AI-powered CV analysis
          </div>

          <h1>
            Find out how well your CV
            <span> matches the job.</span>
          </h1>

          <p>
            Upload your resume and paste an AI
            Engineer job description. Your local AI
            will identify strengths, missing skills
            and interview priorities.
          </p>
        </section>

        <section className="workspace">
          <div className="panel">
            <div className="panel-heading">
              <div>
                <span className="step-number">
                  01
                </span>

                <h2>Upload your CV</h2>
              </div>

              <span className="file-type">
                PDF only
              </span>
            </div>

            <input
              ref={fileInputRef}
              className="hidden-input"
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileChange}
            />

            {!cv ? (
              <button
                type="button"
                className="upload-area"
                onClick={selectFile}
              >
                <div className="upload-icon">
                  ↑
                </div>

                <div className="upload-title">
                  Choose your CV
                </div>

                <div className="upload-description">
                  Select a PDF from your computer
                </div>

                <div className="browse-button">
                  Browse files
                </div>
              </button>
            ) : (
              <div className="selected-file">
                <div className="pdf-icon">
                  PDF
                </div>

                <div className="file-info">
                  <strong>{cv.name}</strong>

                  <span>
                    {(cv.size / 1024).toFixed(1)} KB
                  </span>
                </div>

                <button
                  type="button"
                  className="remove-file"
                  onClick={removeFile}
                  aria-label="Remove file"
                >
                  ×
                </button>
              </div>
            )}
          </div>

          <div className="panel">
            <div className="panel-heading">
              <div>
                <span className="step-number">
                  02
                </span>

                <h2>Job description</h2>
              </div>

              <span className="character-count">
                {jobDescription.length} characters
              </span>
            </div>

            <textarea
              className="job-input"
              value={jobDescription}
              onChange={(event) =>
                setJobDescription(
                  event.target.value
                )
              }
              placeholder="Paste the complete job description here..."
            />
          </div>
        </section>

        {error && (
          <div className="error-message">
            <span>!</span>

            <div>
              <strong>Something needs attention</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        <div className="action-area">
          <button
            type="button"
            className="analyze-button"
            onClick={analyzeMatch}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Analyzing your profile...
              </>
            ) : (
              <>
                <span>✦</span>
                Analyze Match
              </>
            )}
          </button>

          <p>
            Your CV stays on your computer and is
            processed using your local Ollama model.
          </p>
        </div>
    {analysis && (

      <section className="results-section">

        <div className="results-header">

          <div>
            <span className="results-label">
              AI ANALYSIS
            </span>

            <h2>
              Your Match Report
            </h2>
          </div>

          <div className="complete-badge">
            ✓ Analysis complete
          </div>

        </div>


        <ScoreCard
          score={analysis.match_score}
          assessment={
            analysis.final_assessment
          }
        />


        <div className="results-grid">

          <ResultCard
            title="Strong Matches"
            subtitle="Skills clearly supported by your CV"
            icon="✓"
            items={analysis.strong_matches}
            type="positive"
          />

          <ResultCard
            title="Missing Skills"
            subtitle="Requirements not demonstrated yet"
            icon="!"
            items={analysis.missing_skills}
            type="warning"
          />

          <ResultCard
            title="Partial Matches"
            subtitle="Related experience, but not an exact match"
            icon="~"
            items={analysis.partial_matches}
            type="neutral"
          />

        </div>


        <div className="preparation-grid">

          <div className="detail-card">

            <div className="detail-card-header">

              <div>
                <span className="small-label">
                  PREPARATION
                </span>

                <h3>
                  Interview Topics
                </h3>
              </div>

              <span className="detail-count">
                {analysis.interview_topics.length}
              </span>

            </div>


            <div className="interview-list">

              {analysis.interview_topics.map(
                (topic, index) => (

                  <div
                    className="interview-item"
                    key={`${topic}-${index}`}
                  >

                    <div className="topic-number">
                      {String(index + 1)
                        .padStart(2, "0")}
                    </div>

                    <p>
                      {topic}
                    </p>

                  </div>

                )
              )}

            </div>

          </div>


          <div className="detail-card">

            <div className="detail-card-header">

              <div>
                <span className="small-label">
                  NEXT STEPS
                </span>

                <h3>
                  Learning Priorities
                </h3>
              </div>

              <span className="detail-count">
                {analysis.learning_priorities.length}
              </span>

            </div>


            <div className="priority-list">

              {analysis.learning_priorities.map(
                (priority, index) => (

                  <div
                    className="priority-item"
                    key={`${priority}-${index}`}
                  >

                    <div className="priority-number">
                      {index + 1}
                    </div>

                    <div>

                      <span>
                        Priority {index + 1}
                      </span>

                      <p>
                        {priority}
                      </p>

                    </div>

                  </div>

                )
              )}

            </div>

          </div>

        </div>

      </section>

    )}
      </main>

      <footer>
        Built with React · TypeScript · FastAPI ·
        Ollama
      </footer>
    </div>
  );
}

export default App;