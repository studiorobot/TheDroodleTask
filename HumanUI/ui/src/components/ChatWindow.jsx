// import React, { useState, useEffect, useRef } from 'react';
// import '../styles/ChatWindow.css';

// function ChatWindow({ currentImageIndex }) {
//   const [chatHistories, setChatHistories] = useState({
//     0: []
//   });
//   const [input, setInput] = useState('');
//   const [loading, setLoading] = useState(false); // Loading state to show "Forwarding..."
//   const websocket = useRef(null);
//   const lastMessageRef = useRef(null);

//   useEffect(() => {
//     websocket.current = new WebSocket('ws://localhost:8766');

//     websocket.current.onmessage = (event) => {
//       const data = JSON.parse(event.data);

//       setLoading(false); // Stop showing "Forwarding..." when a response is received

//       if (data.message) {
//         const userForwardedMessage = { sender: 'user-forwarded', text: data.message };
//         setChatHistories((prevHistories) => ({
//           ...prevHistories,
//           [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), userForwardedMessage],
//         }));
//       }
//     };

//     return () => {
//       if (websocket.current) {
//         websocket.current.close();
//       }
//     };
//   }, [currentImageIndex]);

//   const currentChatHistory = chatHistories[currentImageIndex] || [];

//   useEffect(() => {
//     if (lastMessageRef.current) {
//       lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
//     }
//   }, [currentChatHistory]);

//   const handleSend = (e) => {
//     e.preventDefault();
//     if (input.trim() !== '') {
//       const userMessage = { sender: 'user', text: input };
//       setChatHistories((prevHistories) => ({
//         ...prevHistories,
//         [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), userMessage],
//       }));

//       if (websocket.current) {
//         websocket.current.send(JSON.stringify({ message: input }));
//         setLoading(true); // Show "Forwarding..." when message is sent
//       }

//       setInput('');
//     }
//   };

//   return (
//     <div className="chat-window">
//       <div className="chat-history">
//         {currentChatHistory.map((msg, idx) => (
//           <div
//             key={idx}
//             className={`chat-message ${
//               msg.sender === 'user' ? 'user' : 'user-forwarded'
//             }`}
//           >
//             <span>{msg.text}</span>
//           </div>
//         ))}
//         {loading && (
//           <div className="chat-message user-forwarded">
//             <span>Forwarding...</span>
//           </div>
//         )}
//         <div ref={lastMessageRef} />
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

import React, { useState, useEffect, useRef } from 'react';
import '../styles/ChatWindow.css';

const initialMessage = "Hello! I’m your AI guide for building a doodle caption. I’m designed to ask you questions and guide your reasoning but if you want to take control of your own creative process, I’ll be happy to help wherever possible.";

function ChatWindow({ currentImageIndex }) {
  const [chatHistories, setChatHistories] = useState({
    0: [{ sender: 'assistant', text: initialMessage }]
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false); // Loading state to show "Forwarding..."
  const websocket = useRef(null);
  const lastMessageRef = useRef(null);

  useEffect(() => {
    websocket.current = new WebSocket('ws://localhost:8766');

    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      setLoading(false); // Stop showing "Forwarding..." when a response is received

      if (data.message) {
        const assistantMessage = { sender: 'assistant', text: data.message };
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
        setLoading(true); // Show "Forwarding..." when message is sent
      }

      setInput('');
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-history">
        {currentChatHistory.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-message ${
              msg.sender === 'user' ? 'user' : 'assistant'
            }`}
          >
            <span>{msg.text}</span>
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <span>Forwarding...</span>
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