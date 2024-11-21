import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatWindow.css';

const initialMessage = "Hello! Need any help with this droodle?";

function ChatWindow({ currentImageIndex }) {
  const [chatHistories, setChatHistories] = useState({
    0: [{ sender: 'assistant', text: initialMessage }]
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false); // Loading state to show "Thinking..."
  const websocket = useRef(null);
  const lastMessageRef = useRef(null);

  useEffect(() => {
    websocket.current = new WebSocket('ws://localhost:8765');

    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      setLoading(false); // Stop showing "Thinking..." when a response is received

      if (data.status === "conversation_reset") {
        setChatHistories((prevHistories) => ({
          ...prevHistories,
          [currentImageIndex]: [
            { sender: 'assistant', text: initialMessage } // First message for the new image
          ]
        }));
      } else if (data.message) {
        const assistantMessage = { sender: data.role, text: data.message };
        setChatHistories((prevHistories) => ({
          ...prevHistories,
          [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), assistantMessage],
        }));
      }
    };

    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, [currentImageIndex]);

  useEffect(() => {
    setChatHistories((prevHistories) => ({
      ...prevHistories,
      [currentImageIndex]: prevHistories[currentImageIndex] || [
        { sender: 'assistant', text: initialMessage }
      ],
    }));
  }, [currentImageIndex]);

  const currentChatHistory = chatHistories[currentImageIndex] || [];

  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentChatHistory]);

  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() !== '') {
      const userMessage = { sender: 'user', text: input };
      setChatHistories((prevHistories) => ({
        ...prevHistories,
        [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), userMessage],
      }));

      if (websocket.current) {
        websocket.current.send(JSON.stringify({ message: input }));
        setLoading(true); // Start showing "Thinking..." when message is sent
      }

      setInput('');
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-history">
        {currentChatHistory.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.sender}`}>
            <span>{msg.text}</span>
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <span>Thinking...</span>
          </div>
        )}
        <div ref={lastMessageRef} />
      </div>
      <form className="chat-input" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default ChatWindow;