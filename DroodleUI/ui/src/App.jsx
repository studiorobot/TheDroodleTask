import React, { useState, useRef, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ImageDisplay from './components/ImageDisplay';
import './styles/App.css';

function App() {
  // State to track the current image index
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const websocket = useRef(null);  // WebSocket reference for communication

  // Establish WebSocket connection
  // useEffect(() => {
  //   websocket.current = new WebSocket('ws://localhost:8765');

  //   // Clean up the WebSocket connection on unmount
  //   return () => {
  //     if (websocket.current) {
  //       websocket.current.close();
  //     }
  //   };
  // }, []);

  useEffect(() => {
    websocket.current = new WebSocket('ws://localhost:8765');
  
    // Handle WebSocket messages
    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === "caption_saved") {
        console.log("Caption saved successfully!");
      } else if (data.status === "error") {
        console.error("Error:", data.message);
      }
    };
  
    // Clean up the WebSocket connection on unmount
    return () => {
      if (websocket.current) {
        websocket.current.close();
      }
    };
  }, []);

  // Function to handle image switching
  // const handleImageSwitch = (newIndex) => {
  //   // Send save and reset command to the WebSocket server
  //   if (websocket.current) {
  //     websocket.current.send(JSON.stringify({ command: "save_and_reset" }));
  //   }
  //   // Update the current image index
  //   setCurrentImageIndex(newIndex);
  // };

  // const handleImageSwitch = (newIndex) => {
  //   console.log(`Switching to image index: ${newIndex}`); // Debugging log
  //   if (websocket.current) {
  //     websocket.current.send(
  //       JSON.stringify({ command: "save_and_reset", switch_image: newIndex })
  //     );
  //   }
  //   setCurrentImageIndex(newIndex); // Update the frontend state
  // };

  const handleImageSwitch = (newIndex, caption = null) => {
    console.log(`Switching to image index: ${newIndex}`); // Debugging log
  
    // If a caption is provided, send it to the backend
    if (caption && websocket.current) {
      websocket.current.send(
        JSON.stringify({
          command: "save_caption",
          imageIndex: currentImageIndex,
          caption: caption,
        })
      );
      console.log(`Caption for image ${currentImageIndex} sent to backend: ${caption}`);
    }
  
    // Notify backend to save and reset, and switch the image
    if (websocket.current) {
      websocket.current.send(
        JSON.stringify({ command: "save_and_reset", switch_image: newIndex })
      );
    }
  
    // Update the frontend state to the new image index
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
        {/* <ImageDisplay 
          currentImageIndex={currentImageIndex} 
          setCurrentImageIndex={setCurrentImageIndex} 
          onImageSwitch={handleImageSwitch} 
        /> */}
        <ImageDisplay
          currentImageIndex={currentImageIndex}
          setCurrentImageIndex={setCurrentImageIndex}
          onImageSwitch={(newIndex, caption) => handleImageSwitch(newIndex, caption)}
        />
      </div>
    </div>
  );
}

export default App;