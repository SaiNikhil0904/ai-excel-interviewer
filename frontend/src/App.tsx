import { useState } from 'react';
import LandingPage from './components/LandingPage';
import InterviewPage from './components/InterviewPage';
import './App.css';

function App() {
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);

  const handleStartInterview = () => {
    setIsInterviewStarted(true);
  };

  const handleEndInterview = () => {
    setIsInterviewStarted(false);
  };

  return (
    <div className="app-container">
      {isInterviewStarted ? (
        <InterviewPage onEndInterview={handleEndInterview} />
      ) : (
        <LandingPage onStartInterview={handleStartInterview} />
      )}
    </div>
  );
}

export default App;