// import React from 'react';
// import '../styles/ImageDisplay.css';
// import abstractImage from '../assets/abstract.png'; // Place your image in src/assets/

// function ImageDisplay() {
//   return (
//     <div className="image-container">
//       <img src={abstractImage} alt="Abstract Art" />
//     </div>
//   );
// }

// export default ImageDisplay;

// //////////////////////////////////////////////////////////////////////////////////////

import React, { useState } from 'react';
import { Rnd } from 'react-rnd';  // Import react-rnd for drag/resize
import '../styles/ImageDisplay.css';
import abstractImage from '../assets/abstract.png';  // Your image

function ImageDisplay() {
  const [rotation, setRotation] = useState(0);  // State for image rotation

  // Handle rotation by updating the rotation state
  const handleRotationChange = (e) => {
    setRotation(e.target.value);
  };

  // Disable native drag behavior
  const handleDragStart = (e) => {
    e.preventDefault();
  };

  return (
    <div className="image-container">
      <Rnd
        default={{
          x: 50,  // Adjusted x position to avoid jumping
          y: 50,  // Adjusted y position to avoid jumping
          width: 200,
          height: 200,
        }}
        minWidth={100}  // Set minimum width/height for resizing
        minHeight={100}
        bounds="parent"  // Ensure the image is draggable within its parent
        lockAspectRatio={true}  // Keep the image aspect ratio while resizing
        dragAxis="both"  // Allow movement in both X and Y directions
      >
        <img
          src={abstractImage}
          alt="Abstract Art"
          className="draggable"
          style={{
            width: '100%',
            height: '100%',
            transform: `rotate(${rotation}deg)`,  // Apply rotation
            cursor: 'move',  // Indicate the image is draggable
          }}
          onDragStart={handleDragStart}  // Disable native drag behavior
        />
      </Rnd>
      <div className="controls">
        <label>Rotate:</label>
        <input
          type="range"
          min="0"
          max="360"
          value={rotation}
          onChange={handleRotationChange}
        />
      </div>
    </div>
  );
}

export default ImageDisplay;