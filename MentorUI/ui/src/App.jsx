// import React, { useState, useRef, useEffect } from 'react';
// import ChatWindow from './components/ChatWindow';
// import ImageDisplay from './components/ImageDisplay';
// import './styles/App.css';

// function App() {
//   // State to track the current image index (synced from the user)
//   const [currentImageIndex, setCurrentImageIndex] = useState(0);
//   const websocket = useRef(null); // WebSocket reference for communication

//   // Establish WebSocket connection (mentor-specific WebSocket server)
//   useEffect(() => {
//     websocket.current = new WebSocket('ws://localhost:8766'); // Connect to mentor WebSocket server

//     websocket.current.onmessage = (event) => {
//       const data = JSON.parse(event.data);
//       // Synchronize image index with updates from the user
//       if (data.status === "image_update") {
//         setCurrentImageIndex(data.imageIndex);
//       }
//     };

//     // Clean up the WebSocket connection on unmount
//     return () => {
//       if (websocket.current) {
//         websocket.current.close();
//       }
//     };
//   }, []);

//   return (
//     <div className="app-container">
//       <div className="left-pane">
//         {/* Pass the WebSocket and role to ChatWindow */}
//         <ChatWindow websocketRef={websocket} isMentor={true} />
//       </div>
//       <div className="right-pane">
//         {/* ImageDisplay only displays the current image index; no controls for switching */}
//         <ImageDisplay currentImageIndex={currentImageIndex} isMentor={true} />
//       </div>
//     </div>
//   );
// }

// export default App;


import React, { useState, useRef, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import ImageDisplay from "./components/ImageDisplay";
import "./styles/App.css";

function App() {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [chatHistories, setChatHistories] = useState({}); // Store droodle-specific chat histories
  const websocket = useRef(null);

  // Establish WebSocket connection for mentor
  useEffect(() => {
    websocket.current = new WebSocket("ws://localhost:8766");
    // websocket.current = new WebSocket('ws://35.3.240.223:8766'); // For mentor

    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === "image_update") {
        const newImageIndex = data.imageIndex;
        setCurrentImageIndex(newImageIndex);

        // Update chat histories if provided
        if (data.chatHistory) {
          setChatHistories((prevHistories) => ({
            ...prevHistories,
            [newImageIndex]: data.chatHistory,
          }));
        }
      } else if (data.role === "user" || data.role === "mentor") {
        // Append message to the current droodle's chat history
        setChatHistories((prevHistories) => ({
          ...prevHistories,
          [currentImageIndex]: [
            ...(prevHistories[currentImageIndex] || []),
            { sender: data.role, text: data.message },
          ],
        }));
      }
    };

    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, [currentImageIndex]);

  return (
    <div className="app-container">
      <div className="left-pane">
        <ChatWindow
          websocketRef={websocket}
          currentImageIndex={currentImageIndex}
          chatHistories={chatHistories}
        />
      </div>
      <div className="right-pane">
        <ImageDisplay currentImageIndex={currentImageIndex} isMentor />
      </div>
    </div>
  );
}

export default App;

