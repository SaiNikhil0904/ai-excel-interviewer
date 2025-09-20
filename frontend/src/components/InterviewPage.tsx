import { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import './InterviewPage.css';

interface Message {
  sender: 'ai' | 'user';
  text: string;
  timestamp?: string;
}

interface StreamEvent {
  type: 'thought' | 'final' | 'error';
  content: string;
  context_id: string; 
}

const BFF_URL = 'http://localhost:8000/api/v1'; 
const AGENT_ID = 'ai_excel_interviewer';

const InterviewPage = ({ onEndInterview }: { onEndInterview: () => void; }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const [progress, setProgress] = useState(0);
  const contextIdRef = useRef<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    handleSendMessage('Start my interview');
  }, []);

  const getTimestamp = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const handleSendMessage = async (text: string) => {
    if (isLoading) return;
    setIsLoading(true);

    if (text !== 'Start my interview') {
      setMessages(prev => [...prev, { sender: 'user', text, timestamp: getTimestamp() }]);
    }
    setUserInput('');

    const aiMessagePlaceholder: Message = { sender: 'ai', text: '...', timestamp: getTimestamp() };
    setMessages(prev => [...prev, aiMessagePlaceholder]);

    try {
      const url = new URL(`${BFF_URL}/chats/${AGENT_ID}/messages`);
      if (contextIdRef.current) {
        url.searchParams.append('context_id', contextIdRef.current);
      }

      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text }),
      });

      if (!response.ok) throw new Error(`Network response was not ok: ${response.statusText}`);
      if (!response.body) throw new Error("Response body is null.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let finalMessageReceived = false;

      while (!finalMessageReceived) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6);
            if (dataStr.trim()) {
              const event: StreamEvent = JSON.parse(dataStr);
              if (!contextIdRef.current && event.context_id) {
                console.log(`Conversation started. Saving contextId: ${event.context_id}`);
                contextIdRef.current = event.context_id;
              }
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage && lastMessage.sender === 'ai') {
                  lastMessage.text = event.content;
                  lastMessage.timestamp = getTimestamp();
                }
                return newMessages;
              });
              
              if (event.type === 'final' || event.type === 'error') {
                finalMessageReceived = true;
                if (event.type === 'final') {
                    const questionMatch = event.content.match(/Question (\d+)/i);
                    if (questionMatch) {
                        const newCount = parseInt(questionMatch[1], 10);
                        setQuestionCount(newCount);
                        setProgress(newCount * 20);
                    }
                }
              }
            }
          }
        }
      }
    } catch (error) {
      const errorText = error instanceof Error ? error.message : 'An unknown error occurred.';
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.sender === 'ai') {
          lastMessage.text = `Sorry, a connection error occurred. Please check the console and ensure all services are running.\n\n*Details: ${errorText}*`;
          lastMessage.timestamp = getTimestamp();
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userInput.trim() && !isLoading) {
      handleSendMessage(userInput.trim());
    }
  };

  return (
    <div className="interview-container">
      <header className="interview-header">
        <h3>Excel Competency Assessment</h3>
        <div className="progress-info">
          {/* ... progress bar JSX ... */}
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
              <div className={`message-bubble ${msg.sender}`} >
                <div dangerouslySetInnerHTML={{ __html: marked.parse(msg.text) as string }} />
              </div>
              <div className="timestamp">{msg.timestamp}</div>
            </div>
          </div>
        ))}
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
          <button type="submit" disabled={isLoading}>➢</button>
        </form>
        <div className="input-footer-text">Press Enter to submit response</div>
      </footer>
    </div>
  );
};

export default InterviewPage;
