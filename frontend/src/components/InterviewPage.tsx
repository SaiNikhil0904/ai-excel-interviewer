import { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import './InterviewPage.css';

interface Message {
  sender: 'ai' | 'user';
  text: string;
  timestamp?: string;
}

const AGENT_A2A_URL = 'http://127.0.0.1:10100';

const InterviewPage = ({ onEndInterview }: { onEndInterview: () => void }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);
  const [contextId, setContextId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    const savedContextId = localStorage.getItem('excel_interviewer_context_id');
    if (savedContextId) {
      setContextId(savedContextId);
    }
    sendMessageToAgent('Start my interview');
  }, []);

  const getTimestamp = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const generateUUID = () => crypto.randomUUID();

  const sendMessageToAgent = async (text: string, retries = 3): Promise<void> => {
    setIsLoading(true);
    if (text !== 'Start my interview') {
      setMessages((prev) => [...prev, { sender: 'user', text, timestamp: getTimestamp() }]);
    }
    setMessages((prev) => [...prev, { sender: 'ai', text: '...', timestamp: getTimestamp() }]);

    try {
      // Align payload with A2A client's structure
      const payload = {
        jsonrpc: '2.0',
        method: 'message.send', // Try 'a2a.message.send' if this fails
        params: {
          message: {
            role: 'user',
            parts: [{ root: { text } }],
            metadata: { user_id: 'web-user' },
            messageId: generateUUID(),
            ...(contextId ? { context_id: contextId } : {}), // Use context_id to match client
          },
        },
        id: Date.now(),
      };

      console.debug('Sending payload:', JSON.stringify(payload, null, 2));

      const response = await fetch(AGENT_A2A_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}, ${await response.text()}`);
      }

      const initialTask = await response.json();
      console.debug('Initial task response:', initialTask);

      if (initialTask.error) {
        throw new Error(`JSON-RPC error: ${initialTask.error.message} (Code: ${initialTask.error.code})`);
      }

      const taskId = initialTask.result?.id;
      if (!taskId) {
        throw new Error('No task ID returned from server');
      }

      if (!contextId && initialTask.result?.context_id) {
        setContextId(initialTask.result.context_id);
        localStorage.setItem('excel_interviewer_context_id', initialTask.result.context_id);
      }

      const finalTask = await pollForResult(taskId);
      const newAIMessageText = finalTask.status?.message?.parts[0]?.root?.text || 'No response text';

      const questionMatch = newAIMessageText.match(/Question (\d+)/i);
      if (questionMatch) {
        const newCount = parseInt(questionMatch[1], 10);
        setQuestionCount(newCount);
        setProgress(newCount * 20); // 5 questions assumed
      }

      setMessages((prev) => [
        ...prev.slice(0, -1),
        { sender: 'ai', text: newAIMessageText, timestamp: getTimestamp() },
      ]);
    } catch (error) {
      console.error('Error in sendMessageToAgent:', error);
      if (retries > 0) {
        console.warn(`Retrying... (${retries} attempts left)`);
        await new Promise((resolve) => setTimeout(resolve, 1000));
        return sendMessageToAgent(text, retries - 1);
      }
      const errorText = error instanceof Error ? error.message : 'Unknown error';
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { sender: 'ai', text: `Error: ${errorText}`, timestamp: getTimestamp() },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const pollForResult = async (taskId: string): Promise<any> => {
    const terminalStates = ['completed', 'failed', 'canceled', 'rejected'];
    for (let i = 0; i < 360; i++) {
      await new Promise((resolve) => setTimeout(resolve, 1000));

      try {
        const res = await fetch(AGENT_A2A_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'task.get', // Try 'a2a.task.get' if this fails
            params: { id: taskId },
            id: Date.now(),
          }),
        });

        if (!res.ok) {
          throw new Error(`HTTP error during polling! Status: ${res.status}, ${await res.text()}`);
        }

        const taskData = await res.json();
        console.debug('Polling response:', taskData);

        if (taskData.error) {
          throw new Error(`JSON-RPC error: ${taskData.error.message} (Code: ${taskData.error.code})`);
        }

        if (!taskData.result) {
          continue;
        }

        const state = taskData.result.status?.state;
        if (terminalStates.includes(state)) {
          return taskData.result;
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }

    throw new Error('Polling timed out.');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userInput.trim() && !isLoading) {
      sendMessageToAgent(userInput.trim());
      setUserInput('');
    }
  };

  return (
    <div className="interview-container">
      <header className="interview-header">
        <h3>Excel Competency Assessment</h3>
        <div className="progress-info">
          <div className="progress-text">
            <span>Assessment Progress: Question {questionCount} of 5</span>
            <span>{progress}% Complete</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
        </div>
        <button onClick={onEndInterview} className="end-button">
          <span>&times;</span> End Assessment
        </button>
      </header>
      <main className="chat-area">
        {messages.map((msg, index) => (
          <div key={index} className={`message-wrapper ${msg.sender}`}>
            {msg.sender === 'ai' && <div className="avatar">🤖</div>}
            <div className="message-content">
              <div className={`message-bubble ${msg.sender}`}>
                <div dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) as string }} />
              </div>
              <div className="timestamp">{msg.timestamp}</div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="loading-spinner">
            <span>Loading...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>
      <footer className="input-area">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Type your response here..."
            disabled={isLoading}
          />
          <div className="input-buttons">
            <button type="submit" disabled={isLoading}>➢</button>
          </div>
        </form>
        <div className="input-footer-text">Press Enter to submit response</div>
      </footer>
    </div>
  );
};

export default InterviewPage;