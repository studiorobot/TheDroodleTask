import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatWindow.css';

function ChatWindow({ currentImageIndex }) {  // Pass the current image index as a prop
  const [chatHistories, setChatHistories] = useState({});  // Object to store chat history for each image
  const [input, setInput] = useState('');  // State to handle user input
  const websocket = useRef(null);  // Ref to store WebSocket instance
  const lastMessageRef = useRef(null);  // Ref to track the last message for auto-scroll

  // Set up WebSocket connection when component mounts
  useEffect(() => {
    websocket.current = new WebSocket('ws://localhost:8765');

    // Handle incoming messages from WebSocket
    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.status === "conversation_reset") {
        // Reset chat history for the new image
        setChatHistories((prevHistories) => ({
          ...prevHistories,
          [currentImageIndex]: []  // Clear chat history for the current image
        }));
      } else if (data.message) {
        // Append received message to the current chat history
        const assistantMessage = { sender: data.role, text: data.message };
        setChatHistories((prevHistories) => ({
          ...prevHistories,
          [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), assistantMessage],
        }));
      }
    };

    // Cleanup WebSocket when component unmounts
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, [currentImageIndex]);  // Re-run when image index changes

  // Load chat history for the current image or initialize it if it doesn't exist
  const currentChatHistory = chatHistories[currentImageIndex] || [];

  // Scroll to the last message whenever messages update
  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentChatHistory]);

  // Handle sending messages to the WebSocket server
  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() !== '') {
      const userMessage = { sender: 'user', text: input };

      // Update chat history for the current image
      setChatHistories((prevHistories) => ({
        ...prevHistories,
        [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), userMessage],
      }));

      // Send the user's message to the WebSocket server
      if (websocket.current) {
        websocket.current.send(JSON.stringify({ message: input }));
      }

      setInput('');  // Clear the input field
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
        {/* Dummy div to act as the scroll target */}
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