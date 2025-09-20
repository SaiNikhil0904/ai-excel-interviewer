import { useState } from 'react';
import LandingPage from './components/LandingPage';
import InterviewPage from './components/InterviewPage';
import './App.css';

function App() {
  const [isInterviewActive, setIsInterviewActive] = useState(false);

  const handleStartInterview = () => {
    setIsInterviewActive(true);
  };

  const handleEndInterview = () => {
    setIsInterviewActive(false);
  };

  return (
    <div className="app-container">
      {isInterviewActive ? (
        <InterviewPage onEndInterview={handleEndInterview} />
      ) : (
        <LandingPage onStartInterview={handleStartInterview} />
      )}
    </div>
  );
}

export default App;
