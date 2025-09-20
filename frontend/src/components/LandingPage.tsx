import './LandingPage.css';

interface LandingPageProps {
  onStartInterview: () => void;
}

const LandingPage = ({ onStartInterview }: LandingPageProps) => {
  return (
    <div className="landing-container">
      {/* --- Top Navigation Bar --- */}
      <nav className="landing-nav">
        <div className="logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" />
            <path d="M14 2V8H20" />
            <path d="M16 13H8" /><path d="M16 17H8" /><path d="M10 9H8" />
          </svg>
          <span>Excel AI Interviewer</span>
        </div>
      </nav>

      {/* --- Main Hero Section --- */}
      <main className="hero-section">
        <div className="brand-by">by CodingNinjas</div>
        <h1>AI Excel Interviewer</h1>
        <p className="subtitle">
          Revolutionize your hiring process with our AI-powered Excel interviewer.
          <br />
          Conduct standardized, unbiased interviews that accurately assess candidates' Excel competencies.
        </p>
        
        <div className="start-box">
          <h2>Start Interview Process</h2>
          <p>Begin conducting professional Excel competency assessments</p>
          <button className="start-button" onClick={onStartInterview}>Conduct Interview</button>
          <span className="time-note">&#128337; Complete assessment in 10-15 minutes</span>
        </div>
      </main>

      {/* --- Features Section --- */}
      <section className="features-grid">
        <div className="feature-card">
          <div className="icon"><img src="https://img.icons8.com/fluency/48/brain.png" alt="AI Brain Icon"/></div>
          <h3>AI-Powered Assessment</h3>
          <p>Intelligent evaluation of Excel skills with consistent, unbiased scoring.</p>
        </div>
        <div className="feature-card">
          <div className="icon"><img src="https://img.icons8.com/fluency/48/document.png" alt="Document Icon"/></div>
          <h3>Real-World Scenarios</h3>
          <p>Job-relevant Excel challenges tailored to your specific role requirements.</p>
        </div>
        <div className="feature-card">
          <div className="icon"><img src="https://img.icons8.com/fluency/48/target.png" alt="Target Icon"/></div>
          <h3>Automated Scoring</h3>
          <p>Instant candidate evaluation with detailed competency breakdown.</p>
        </div>
        <div className="feature-card">
          <div className="icon"><img src="https://img.icons8.com/fluency/48/combo-chart.png" alt="Chart Icon"/></div>
          <h3>Standardized Process</h3>
          <p>Consistent interview experience for all candidates.</p>
        </div>
      </section>

      <section className="how-it-works">
        <h2>How Our AI Interviewer Works</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Candidate Setup</h3>
            <p>Candidate begins the structured Excel competency assessment.</p>
          </div>
          <div className="step-arrow">&rarr;</div>
          <div className="step">
            <div className="step-number">2</div>
            <h3>AI Assessment</h3>
            <p>Our AI conducts comprehensive Excel evaluation with adaptive questioning.</p>
          </div>
          <div className="step-arrow">&rarr;</div>
          <div className="step">
            <div className="step-number">3</div>
            <h3>Instant Results</h3>
            <p>Receive comprehensive candidate evaluation with hiring recommendations.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
