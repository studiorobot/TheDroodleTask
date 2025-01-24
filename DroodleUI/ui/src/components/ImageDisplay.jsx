// import React, { useState, useRef } from 'react';
// import { Rnd } from 'react-rnd';  // Import react-rnd for drag/resize
// import '../styles/ImageDisplay.css';
// import abstractImage1 from '../../../../droodleExamples/droodleExample.jpg';  // First image
// import abstractImage2 from '../../../../droodleExamples/droodleExample2.jpg';  // Second image
// import abstractImage3 from '../../../../droodleExamples/droodleExample3.jpg';  // Third image
// import abstractImage4 from '../../../../droodleExamples/droodleExample4.jpg';  // Fourth image

// function ImageDisplay({ currentImageIndex, setCurrentImageIndex, onImageSwitch }) {
//   const images = [abstractImage1, abstractImage2, abstractImage3, abstractImage4]; // Array of images

//   // State to store the rotation, position, and size of each image
//   const [imageStates, setImageStates] = useState(() => {
//     return images.map(() => ({
//       rotation: 0,
//       position: { x: 50, y: 50 },
//       size: { width: 200, height: 200 }
//     }));
//   });

//   const [isHoveringCorner, setIsHoveringCorner] = useState(false);  // State for showing rotation icon
//   const [isRotating, setIsRotating] = useState(false);  // State to track if the image is being rotated
//   const rndRef = useRef(null);  // Reference to Rnd component

//   // Handle rotation based on dragging at corners
//   const handleRotateStart = (e) => {
//     setIsRotating(true);  // Set rotating state to true when rotation starts
//     const initialMouseY = e.clientY;
//     const initialRotation = imageStates[currentImageIndex].rotation;

//     const handleMouseMove = (moveEvent) => {
//       const deltaY = moveEvent.clientY - initialMouseY;
//       const newRotation = initialRotation + deltaY * 0.3;  // Adjust rotation sensitivity

//       // Update rotation in the state
//       setImageStates(prevState => {
//         const newState = [...prevState];
//         newState[currentImageIndex].rotation = newRotation;
//         return newState;
//       });
//     };

//     const handleMouseUp = () => {
//       setIsRotating(false);  // Set rotating state to false when rotation ends
//       document.removeEventListener('mousemove', handleMouseMove);
//       document.removeEventListener('mouseup', handleMouseUp);
//     };

//     // Listen for mouse movement and mouse release
//     document.addEventListener('mousemove', handleMouseMove);
//     document.addEventListener('mouseup', handleMouseUp);
//   };

//   // Handle drag stop to update position
//   const handleDragStop = (e, d) => {
//     if (!isRotating) {
//       setImageStates(prevState => {
//         const newState = [...prevState];
//         newState[currentImageIndex].position = { x: d.x, y: d.y };
//         return newState;
//       });
//     }
//   };

//   // Handle resize stop to update size
//   const handleResizeStop = (e, direction, ref, delta, position) => {
//     if (!isRotating) {
//       setImageStates(prevState => {
//         const newState = [...prevState];
//         newState[currentImageIndex].size = {
//           width: ref.offsetWidth,
//           height: ref.offsetHeight
//         };
//         newState[currentImageIndex].position = position;  // Update position in case it changes during resize
//         return newState;
//       });
//     }
//   };

//   // // Navigate to the next image
//   // const handleNextImage = () => {
//   //   const nextIndex = (currentImageIndex + 1) % images.length; // Loop back to first image if at the end
//   //   setCurrentImageIndex(nextIndex);
//   //   onImageSwitch(nextIndex);  // Notify parent about the image switch
//   // };

//   // // Navigate to the previous image
//   // const handlePreviousImage = () => {
//   //   const prevIndex = (currentImageIndex - 1 + images.length) % images.length; // Loop back to last image if at the beginning
//   //   setCurrentImageIndex(prevIndex);
//   //   onImageSwitch(prevIndex);  // Notify parent about the image switch
//   // };

//   // Navigate to the next image
// const handleNextImage = () => {
//   const nextIndex = (currentImageIndex + 1) % images.length; // Loop back to the first image if at the end
//   onImageSwitch(nextIndex); // Notify the parent (App.jsx) about the image switch, which updates the state
// };

// // Navigate to the previous image
// const handlePreviousImage = () => {
//   const prevIndex = (currentImageIndex - 1 + images.length) % images.length; // Loop back to the last image if at the beginning
//   onImageSwitch(prevIndex); // Notify the parent (App.jsx) about the image switch, which updates the state
// };

//   const currentImageState = imageStates[currentImageIndex];  // Get the state for the current image

//   return (
//     <div className="image-container" style={{ userSelect: 'none' }}>
//       <button 
//         onClick={handlePreviousImage} 
//         className="prev-button"
//         disabled={currentImageIndex === 0}  // Disable if the first image is active
//       >
//         ←
//       </button>
//       <Rnd
//         ref={rndRef}  // Reference to Rnd component
//         size={currentImageState.size}  // Set size from state
//         position={currentImageState.position}  // Set position from state
//         onDragStart={(e) => {
//           if (isRotating) {
//             e.preventDefault();  // Prevent dragging while rotating
//           }
//         }}
//         onDragStop={handleDragStop}  // Update position in state
//         onResizeStart={(e) => {
//           if (isRotating) {
//             e.preventDefault();  // Prevent resizing while rotating
//           }
//         }}
//         onResizeStop={handleResizeStop}  // Update size and position in state
//         disableDragging={isRotating}  // Disable dragging while rotating
//         minWidth={100}
//         minHeight={100}
//         bounds="parent"
//         lockAspectRatio={true}  // Keep the image aspect ratio while resizing
//       >
//         <div
//           style={{
//             width: '100%',
//             height: '100%',
//             transform: `rotate(${currentImageState.rotation}deg)`,  // Rotate the image
//             position: 'relative',
//             userSelect: 'none',
//           }}
//         >
//           <img
//             src={images[currentImageIndex]}
//             alt="Abstract Art"
//             style={{
//               width: '100%',
//               height: '100%',
//               objectFit: 'contain',
//               userSelect: 'none',
//               pointerEvents: 'none',  // Disable native drag on the image
//             }}
//           />
//           {/* Rotation corners */}
//           <div
//             className="rotate-corner"
//             style={{
//               position: 'absolute',
//               top: '-10px',
//               left: '-10px',
//               cursor: 'pointer',
//               opacity: isHoveringCorner ? 1 : 0,  // Show icon only on hover
//             }}
//             onMouseEnter={() => setIsHoveringCorner(true)}
//             onMouseLeave={() => setIsHoveringCorner(false)}
//             onMouseDown={handleRotateStart}
//           >
//             ⟲
//           </div>
//           <div
//             className="rotate-corner"
//             style={{
//               position: 'absolute',
//               top: '-10px',
//               right: '-10px',
//               cursor: 'pointer',
//               opacity: isHoveringCorner ? 1 : 0,  // Show icon only on hover
//             }}
//             onMouseEnter={() => setIsHoveringCorner(true)}
//             onMouseLeave={() => setIsHoveringCorner(false)}
//             onMouseDown={handleRotateStart}
//           >
//             ⟲
//           </div>
//           <div
//             className="rotate-corner"
//             style={{
//               position: 'absolute',
//               bottom: '-10px',
//               left: '-10px',
//               cursor: 'pointer',
//               opacity: isHoveringCorner ? 1 : 0,  // Show icon only on hover
//             }}
//             onMouseEnter={() => setIsHoveringCorner(true)}
//             onMouseLeave={() => setIsHoveringCorner(false)}
//             onMouseDown={handleRotateStart}
//           >
//             ⟲
//           </div>
//           <div
//             className="rotate-corner"
//             style={{
//               position: 'absolute',
//               bottom: '-10px',
//               right: '-10px',
//               cursor: 'pointer',
//               opacity: isHoveringCorner ? 1 : 0,  // Show icon only on hover
//             }}
//             onMouseEnter={() => setIsHoveringCorner(true)}
//             onMouseLeave={() => setIsHoveringCorner(false)}
//             onMouseDown={handleRotateStart}
//           >
//             ⟲
//           </div>
//         </div>
//       </Rnd>
//       <button 
//         onClick={handleNextImage} 
//         className="next-button"
//         disabled={currentImageIndex === images.length - 1}  // Disable if the last image is active
//       >
//         →
//       </button>
//     </div>
//   );
// }

// export default ImageDisplay;



////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////

import React, { useState, useRef } from 'react';
import { Rnd } from 'react-rnd';  // Import react-rnd for drag/resize
import '../styles/ImageDisplay.css';
import abstractImage1 from '../../../../droodleExamples/droodleExample.jpg';  // First image
import abstractImage2 from '../../../../droodleExamples/droodleExample2.jpg';  // Second image
import abstractImage3 from '../../../../droodleExamples/droodleExample3.jpg';  // Third image
import abstractImage4 from '../../../../droodleExamples/droodleExample4.jpg';  // Fourth image

function ImageDisplay({ currentImageIndex, setCurrentImageIndex, onImageSwitch }) {
  const images = [abstractImage1, abstractImage2, abstractImage3, abstractImage4]; // Array of images

  // State to store the rotation, position, and size of each image
  const [imageStates, setImageStates] = useState(() => {
    return images.map(() => ({
      rotation: 0,
      position: { x: 300, y: 400 },
      size: { width: 500, height: 500 }
    }));
  });

  const [isHoveringCorner, setIsHoveringCorner] = useState(false);  // State for showing rotation icon
  const [isRotating, setIsRotating] = useState(false);  // State to track if the image is being rotated
  const rndRef = useRef(null);  // Reference to Rnd component

  // State for caption and submission status
  const [caption, setCaption] = useState('');
  const [isCaptionSubmitted, setIsCaptionSubmitted] = useState(false);

  // Handle rotation based on dragging at corners
  // const handleRotateStart = (e) => {
  //   setIsRotating(true);  // Set rotating state to true when rotation starts
  //   const initialMouseY = e.clientY;
  //   const initialRotation = imageStates[currentImageIndex].rotation;

  //   const handleMouseMove = (moveEvent) => {
  //     const deltaY = moveEvent.clientY - initialMouseY;
  //     const newRotation = initialRotation + deltaY * 0.3;  // Adjust rotation sensitivity

  //     // Update rotation in the state
  //     setImageStates(prevState => {
  //       const newState = [...prevState];
  //       newState[currentImageIndex].rotation = newRotation;
  //       return newState;
  //     });
  //   };

  //   const handleMouseUp = () => {
  //     setIsRotating(false);  // Set rotating state to false when rotation ends
  //     document.removeEventListener('mousemove', handleMouseMove);
  //     document.removeEventListener('mouseup', handleMouseUp);
  //   };

  //   // Listen for mouse movement and mouse release
  //   document.addEventListener('mousemove', handleMouseMove);
  //   document.addEventListener('mouseup', handleMouseUp);
  // };

  const handleRotateStart = (e) => {
    setIsRotating(true);  // Enable rotation
    const initialMouseY = e.clientY;
    const initialRotation = imageStates[currentImageIndex].rotation;
  
    const handleMouseMove = (moveEvent) => {
      const deltaY = moveEvent.clientY - initialMouseY;
      const newRotation = initialRotation + deltaY * 0.3; // Adjust sensitivity
      setImageStates(prevState => {
        const newState = [...prevState];
        newState[currentImageIndex].rotation = newRotation;
        return newState;
      });
    };
  
    const handleMouseUp = () => {
      setIsRotating(false);  // Disable rotation
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  
    // Add listeners
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // Handle drag stop to update position
  const handleDragStop = (e, d) => {
    if (!isRotating) {
      setImageStates(prevState => {
        const newState = [...prevState];
        newState[currentImageIndex].position = { x: d.x, y: d.y };
        return newState;
      });
    }
  };

  // Handle resize stop to update size
  const handleResizeStop = (e, direction, ref, delta, position) => {
    if (!isRotating) {
      setImageStates(prevState => {
        const newState = [...prevState];
        newState[currentImageIndex].size = {
          width: ref.offsetWidth,
          height: ref.offsetHeight
        };
        newState[currentImageIndex].position = position;  // Update position in case it changes during resize
        return newState;
      });
    }
  };

  // Handle caption input
  const handleCaptionChange = (e) => setCaption(e.target.value);

  // const handleSubmitCaption = () => {
  //   if (caption.trim()) {
  //     setIsCaptionSubmitted(true);
  
  //     // Send the caption and current image index to the parent (App.jsx)
  //     if (onImageSwitch) {
  //       onImageSwitch(currentImageIndex, caption.trim());
  //     }
  //   } else {
  //     alert("Please type a caption before proceeding.");
  //   }
  // };

  const saveCaptionToJSON = (imageIndex, caption) => {
    const data = {
      content: caption,
      timestamp: new Date().toISOString(),
      role: "caption", // Denotes this is the final caption
      image_path: images[imageIndex], // Path to the image
      assistant_type: "LLM",
      note: "Official Caption",
    };
  
    const jsonString = JSON.stringify(data, null, 2); // Format JSON with 2-space indentation
    const sessionNumber = "0"
    const fileName = `pilotStudies_finalCaptions_Session_${sessionNumber}_image_${imageIndex}_caption.json`;
  
    // Create a Blob and trigger download
    const blob = new Blob([jsonString], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    link.click();
  
    console.log(`Caption saved locally for image ${imageIndex}:`, data);
  };

  const handleSubmitCaption = () => {
    if (caption.trim()) {
      setIsCaptionSubmitted(true);
  
      // Save the caption to JSON
      saveCaptionToJSON(currentImageIndex, caption.trim());
  
      // Notify the parent about the image switch
      if (onImageSwitch) {
        onImageSwitch(currentImageIndex, caption.trim());
      }
    } else {
      alert("Please type a caption before proceeding.");
    }
  };

  // Navigate to the next image
  // const handleNextImage = () => {
  //   if (isCaptionSubmitted) {
  //     const nextIndex = (currentImageIndex + 1) % images.length; // Loop back to the first image if at the end
  //     onImageSwitch(nextIndex); // Notify parent about the image switch
  //     setCaption(''); // Reset caption
  //     setIsCaptionSubmitted(false); // Reset submission status
  //   }
  // };

  const handleNextImage = () => {
    if (isCaptionSubmitted) {
      const nextIndex = (currentImageIndex + 1) % images.length; // Loop back to the first image if at the end
      onImageSwitch(nextIndex, caption.trim()); // Send the current caption before switching
      setCaption(''); // Reset caption
      setIsCaptionSubmitted(false); // Reset submission status
    }
  };

  const currentImageState = imageStates[currentImageIndex];  // Get the state for the current image

//   return (
//     <div className="image-container" style={{ userSelect: 'none' }}>
//       <Rnd
//         ref={rndRef}  // Reference to Rnd component
//         size={currentImageState.size}  // Set size from state
//         position={currentImageState.position}  // Set position from state
//         onDragStart={(e) => {
//           if (isRotating) {
//             e.preventDefault();  // Prevent dragging while rotating
//           }
//         }}
//         onDragStop={handleDragStop}  // Update position in state
//         onResizeStart={(e) => {
//           if (isRotating) {
//             e.preventDefault();  // Prevent resizing while rotating
//           }
//         }}
//         onResizeStop={handleResizeStop}  // Update size and position in state
//         disableDragging={isRotating}  // Disable dragging while rotating
//         minWidth={100}
//         minHeight={100}
//         bounds="parent"
//         lockAspectRatio={true}  // Keep the image aspect ratio while resizing
//       >
//         <div
//           style={{
//             width: '100%',
//             height: '100%',
//             transform: `rotate(${currentImageState.rotation}deg)`,  // Rotate the image
//             position: 'relative',
//             userSelect: 'none',
//           }}
//         >
//           <img
//             src={images[currentImageIndex]}
//             alt="Abstract Art"
//             style={{
//               width: '100%',
//               height: '100%',
//               objectFit: 'contain',
//               userSelect: 'none',
//               pointerEvents: 'none',  // Disable native drag on the image
//             }}
//           />
//         </div>
//       </Rnd>
//       {/* Caption Input */}
//       <div className="caption-box">
//         <label htmlFor="caption">Please type the final caption here:</label>
//         <textarea
//           id="caption"
//           value={caption}
//           onChange={handleCaptionChange}
//           rows="3"
//           style={{ width: '100%', marginTop: '10px' }}
//           disabled={isCaptionSubmitted} // Disable input if caption is submitted
//         ></textarea>
//         <button
//           onClick={handleSubmitCaption}
//           disabled={isCaptionSubmitted} // Disable button if caption is submitted
//           style={{ marginTop: '10px' }}
//         >
//           Done
//         </button>
//       </div>
//       {/* Next Button */}
//       <button
//         onClick={handleNextImage}
//         className="next-button"
//         disabled={!isCaptionSubmitted} // Disable "Next" until caption is submitted
//         style={{ marginTop: '20px' }}
//       >
//         Next →
//       </button>
//     </div>
//   );
// }

return (
  <div className="image-container" style={{ userSelect: 'none' }}>
    <Rnd
      ref={rndRef} // Reference to Rnd component
      size={currentImageState.size} // Set size from state
      position={currentImageState.position} // Set position from state
      onDragStart={(e) => {
        if (isRotating) {
          e.preventDefault(); // Prevent dragging while rotating
        }
      }}
      onDragStop={handleDragStop} // Update position in state
      onResizeStart={(e) => {
        if (isRotating) {
          e.preventDefault(); // Prevent resizing while rotating
        }
      }}
      onResizeStop={handleResizeStop} // Update size and position in state
      disableDragging={isRotating} // Disable dragging while rotating
      minWidth={100}
      minHeight={100}
      bounds="parent"
      lockAspectRatio={true} // Keep the image aspect ratio while resizing
    >
      <div
        style={{
          width: '100%',
          height: '100%',
          transform: `rotate(${currentImageState.rotation}deg)`, // Rotate the image
          position: 'relative',
          userSelect: 'none',
        }}
      >
        <img
          src={images[currentImageIndex]}
          alt="Abstract Art"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            userSelect: 'none',
            pointerEvents: 'none', // Disable native drag on the image
          }}
        />
        {/* Rotation corners */}
        <div
          className="rotate-corner"
          style={{
            position: 'absolute',
            top: '-10px',
            left: '-10px',
            cursor: 'pointer',
            opacity: isHoveringCorner ? 1 : 0, // Show icon only on hover
          }}
          onMouseEnter={() => setIsHoveringCorner(true)}
          onMouseLeave={() => setIsHoveringCorner(false)}
          onMouseDown={handleRotateStart} // Start rotation
        >
          ⟲
        </div>
        <div
          className="rotate-corner"
          style={{
            position: 'absolute',
            top: '-10px',
            right: '-10px',
            cursor: 'pointer',
            opacity: isHoveringCorner ? 1 : 0,
          }}
          onMouseEnter={() => setIsHoveringCorner(true)}
          onMouseLeave={() => setIsHoveringCorner(false)}
          onMouseDown={handleRotateStart}
        >
          ⟲
        </div>
        <div
          className="rotate-corner"
          style={{
            position: 'absolute',
            bottom: '-10px',
            left: '-10px',
            cursor: 'pointer',
            opacity: isHoveringCorner ? 1 : 0,
          }}
          onMouseEnter={() => setIsHoveringCorner(true)}
          onMouseLeave={() => setIsHoveringCorner(false)}
          onMouseDown={handleRotateStart}
        >
          ⟲
        </div>
        <div
          className="rotate-corner"
          style={{
            position: 'absolute',
            bottom: '-10px',
            right: '-10px',
            cursor: 'pointer',
            opacity: isHoveringCorner ? 1 : 0,
          }}
          onMouseEnter={() => setIsHoveringCorner(true)}
          onMouseLeave={() => setIsHoveringCorner(false)}
          onMouseDown={handleRotateStart}
        >
          ⟲
        </div>
      </div>
    </Rnd>
    {/* Caption Input */}
    <div className="caption-box">
      <label htmlFor="caption">Please type the final caption here:</label>
      <textarea
        id="caption"
        value={caption}
        onChange={handleCaptionChange}
        rows="3"
        style={{ width: '100%', marginTop: '10px' }}
        disabled={isCaptionSubmitted} // Disable input if caption is submitted
      ></textarea>
      <button
        onClick={handleSubmitCaption}
        disabled={isCaptionSubmitted} // Disable button if caption is submitted
        style={{ marginTop: '10px' }}
      >
        Done
      </button>
    </div>
    {/* Next Button */}
    <button
      onClick={handleNextImage}
      className="next-button"
      disabled={!isCaptionSubmitted} // Disable "Next" until caption is submitted
      style={{ marginTop: '20px' }}
    >
      Next →
    </button>
  </div>
);
}

export default ImageDisplay;