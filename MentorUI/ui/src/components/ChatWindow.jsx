// import React, { useState, useEffect, useRef } from 'react';
// import '../styles/ChatWindow.css';

// function ChatWindow() {
//   const [chatHistories, setChatHistories] = useState([]);
//   const [input, setInput] = useState('');
//   const websocket = useRef(null);
//   const lastMessageRef = useRef(null);

//   useEffect(() => {
//     websocket.current = new WebSocket('ws://localhost:8766'); // Mentor-specific WebSocket
//     // websocket.current = new WebSocket('ws://35.3.184.234:8766'); // For mentor

//     websocket.current.onmessage = (event) => {
//       const data = JSON.parse(event.data);

//       if (data.message) {
//         const newMessage = { sender: data.role, text: data.message };
//         setChatHistories((prevMessages) => [...prevMessages, newMessage]);
//       }
//     };

//     return () => {
//       if (websocket.current) {
//         websocket.current.close();
//       }
//     };
//   }, []);

//   useEffect(() => {
//     if (lastMessageRef.current) {
//       lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
//     }
//   }, [chatHistories]);

//   const handleSend = (e) => {
//     e.preventDefault();
//     if (input.trim() !== '') {
//       const mentorMessage = { sender: 'mentor', text: input };

//       // Add the message to the chat history
//       setChatHistories((prevMessages) => [...prevMessages, mentorMessage]);

//       // Send the message through the WebSocket
//       if (websocket.current) {
//         websocket.current.send(JSON.stringify({ message: input }));
//       }

//       setInput(''); // Clear the input box
//     }
//   };

//   return (
//     <div className="chat-window">
//       <div className="chat-history">
//         {chatHistories.map((msg, idx) => (
//           <div key={idx} className={`chat-message ${msg.sender}`}>
//             <span>{msg.text}</span>
//           </div>
//         ))}
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


function ChatWindow({ websocketRef, currentImageIndex, chatHistories, setChatHistories }) {
  const [input, setInput] = useState('');
  const lastMessageRef = useRef(null);

  const currentChatHistory = chatHistories[currentImageIndex] || [];

  // Auto-scroll to the latest message
  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [currentChatHistory]);

  useEffect(() => {
    if (websocketRef.current) {
      websocketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.role === 'mentor' || data.role === 'grammarcorrection') {
          const message = { sender: data.role, text: data.message };
          setChatHistories((prevHistories) => ({
            ...prevHistories,
            [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), message],
          }));
        }
      };
    }
  }, [currentImageIndex, setChatHistories]);

  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim() !== '') {
      const mentorMessage = { sender: 'mentor', text: input };

      // Update chat history immediately so mentor sees their own message
      setChatHistories((prevHistories) => ({
        ...prevHistories,
        [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), mentorMessage],
      }));

      // Send the message via WebSocket
      if (websocketRef.current) {
        websocketRef.current.send(JSON.stringify({ message: input }));
      }
      
      // Update chat history immediately so mentor sees their own message
      // setChatHistories((prevHistories) => ({
      //   ...prevHistories,
      //   [currentImageIndex]: [...(prevHistories[currentImageIndex] || []), mentorMessage],
      // }));
      
      setInput(''); // Clear input field after sending
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
