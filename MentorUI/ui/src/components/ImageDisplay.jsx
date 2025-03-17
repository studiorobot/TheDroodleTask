import React, { useState, useRef, useEffect } from 'react';
import { Rnd } from 'react-rnd';
import '../styles/ImageDisplay.css';
import abstractImage1 from '../../../../droodleExamples/droodleExample1.jpg';
import abstractImage2 from '../../../../droodleExamples/droodleExample2.jpg';
import abstractImage3 from '../../../../droodleExamples/droodleExample3.jpg';
import abstractImage4 from '../../../../droodleExamples/droodleExample4.jpg';
import config from '../../../../config.json';

const imageMap = {
  'abstractImage1': abstractImage1,
  'abstractImage2': abstractImage2,
  'abstractImage3': abstractImage3,
  'abstractImage4': abstractImage4,
};

function ImageDisplay({ currentImageIndex, setCurrentImageIndex, onImageSwitch, isMentor = false }) {
  // const images = [abstractImage1, abstractImage2, abstractImage3, abstractImage4];
  // const images = [['abstractImage3', 'abstractImage4', 'abstractImage1', 'abstractImage2']];
  // const imageNames = ['abstractImage3', 'abstractImage4', 'abstractImage2', 'abstractImage1'];
  
  const imageNames = config.jsx_images;
  const images = imageNames.map(name => imageMap[name]);

  const [imageStates, setImageStates] = useState(() => {
    return images.map(() => ({
      rotation: 0,
      position: { x: 0, y: 0 },
      size: { width: 350, height: 350 }
    }));
  });

  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      const containerWidth = containerRef.current.clientWidth;
      const containerHeight = containerRef.current.clientHeight;
      const imageWidth = imageStates[0].size.width;
      const imageHeight = imageStates[0].size.height;

      const centerX = (containerWidth - imageWidth) / 2;
      const centerY = (containerHeight - imageHeight) / 2;

      setImageStates((prevStates) =>
        prevStates.map((state) => ({
          ...state,
          position: { x: centerX, y: centerY }
        }))
      );
    }
  }, []);

  return (
    <div ref={containerRef} className="image-container">
      <Rnd
        size={imageStates[currentImageIndex].size}
        position={imageStates[currentImageIndex].position}
        disableDragging={true}
        lockAspectRatio={true}
      >
        <img src={images[currentImageIndex]} alt="Abstract Art" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
      </Rnd>
      
      {!isMentor && (
        <div className="button-container">
          <button onClick={() => onImageSwitch(currentImageIndex - 1, "previous")} disabled={currentImageIndex === 0}>←</button>
          <button onClick={() => onImageSwitch(currentImageIndex + 1, "next")} disabled={currentImageIndex === images.length - 1}>→</button>
        </div>
      )}
    </div>
  );
}

export default ImageDisplay;

/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////