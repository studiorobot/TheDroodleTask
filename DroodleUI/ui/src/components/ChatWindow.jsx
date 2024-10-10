// import React, { useState } from 'react';
// import '../styles/ChatWindow.css';

// function ChatWindow() {
//   const [messages, setMessages] = useState([
//     { sender: 'assistant', text: 'Hello! Need help with captions?' },
//   ]);
//   const [input, setInput] = useState('');

//   const handleSend = (e) => {
//     e.preventDefault();
//     if (input.trim() !== '') {
//       const userMessage = { sender: 'user', text: input };
//       setMessages([...messages, userMessage]);
//       setInput('');
//       // TODO: Implement API call and handle assistant's response
//     }
//   };

//   return (
//     <div className="chat-window">
//       <div className="chat-history">
//         {messages.map((msg, idx) => (
//           <div key={idx} className={`chat-message ${msg.sender}`}>
//             <span>{msg.text}</span>
//           </div>
//         ))}
//       </div>
//       <form className="chat-input" onSubmit={handleSend}>
//         <input
//           type="text"
//           placeholder="Type your message..."
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//         />
//         <button type="submit">Send</button>
//       </form>
//     </div>
//   );
// }

// export default ChatWindow;

//////////////////////////////////////////////////////////////////////////////////////
import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatWindow.css';

function ChatWindow() {
  const [messages, setMessages] = useState([
    { sender: 'assistant', text: 'Hello! Need help with captions?' },
  ]);
  const [input, setInput] = useState('');
  const websocket = useRef(null); // Ref to store WebSocket instance
  const lastMessageRef = useRef(null); // Ref to track the last message for auto-scroll

  // Set up WebSocket connection when component mounts
  useEffect(() => {
    // Initialize WebSocket connection
    websocket.current = new WebSocket('ws://localhost:8765');

    // Handle incoming messages from WebSocket
    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const assistantMessage = { sender: data.role, text: data.message };
      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    };

    // Cleanup WebSocket when component unmounts
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);

  // Scroll to the last message whenever messages update
  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Handle sending messages to the WebSocket server
  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() !== '') {
      const userMessage = { sender: 'user', text: input };
      setMessages((prevMessages) => [...prevMessages, userMessage]);

      // Send the user's message to the WebSocket server
      if (websocket.current) {
        websocket.current.send(JSON.stringify({ message: input }));
      }

      setInput('');
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-history">
        {messages.map((msg, idx) => (
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