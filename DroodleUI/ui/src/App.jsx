import React, { useState, useRef, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ImageDisplay from './components/ImageDisplay';
import './styles/App.css';

function App() {
  // State to track the current image index
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const websocket = useRef(null);  // WebSocket reference for communication

  // Establish WebSocket connection
  useEffect(() => {
    websocket.current = new WebSocket('ws://localhost:8765');
    // websocket.current = new WebSocket("ws://35.3.184.234:8765");

    // Clean up the WebSocket connection on unmount
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);

  // Function to handle caption submission
  const handleCaptionSubmit = (caption) => {
    if (websocket.current) {
      websocket.current.send(JSON.stringify({
        command: "submit_caption",
        caption: caption,
        imageIndex: currentImageIndex
      }));
    }
  };

  // Function to handle image switching
  const handleImageSwitch = (newIndex, direction) => {
    // Send save and reset command to the WebSocket server
    // if (websocket.current) {
    //   websocket.current.send(JSON.stringify({ command: "save_and_reset" }));
    // }

    if (websocket.current) {
      websocket.current.send(
        JSON.stringify({
          command: "save_and_reset",
          switch_image: newIndex,
          direction: direction // Send "next" or "previous"
        })
      );
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
          onSubmitCaption={handleCaptionSubmit}
        />
      </div>
    </div>
  );
}

export default App;