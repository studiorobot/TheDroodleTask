import React, { useState, useRef, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ImageDisplay from './components/ImageDisplay';
import './styles/App.css';

function App() {
  // State to track the current image index
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const websocket = useRef(null);  // WebSocket reference for communication

  // Establish WebSocket connection to the humanAgentUI server on port 8766
  useEffect(() => {
    websocket.current = new WebSocket('ws://localhost:8766');

    // Clean up the WebSocket connection on unmount
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);

  // Function to handle image switching
  const handleImageSwitch = (newIndex) => {
    // Send save and reset command to the WebSocket server
    if (websocket.current) {
      websocket.current.send(JSON.stringify({ command: "save_and_reset" }));
    }
    // Update the current image index
    setCurrentImageIndex(newIndex);
  };

  return (
    <div className="app-container">
      <div className="left-pane">
        {/* Pass currentImageIndex to ChatWindow */}
        <ChatWindow currentImageIndex={currentImageIndex} />
      </div>
      <div className="right-pane">
        {/* Pass currentImageIndex, setCurrentImageIndex, and handleImageSwitch to ImageDisplay */}
        <ImageDisplay 
          currentImageIndex={currentImageIndex} 
          setCurrentImageIndex={setCurrentImageIndex} 
          onImageSwitch={handleImageSwitch} 
        />
      </div>
    </div>
  );
}

export default App;